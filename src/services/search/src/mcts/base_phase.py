import asyncio
import os
from datetime import datetime
from typing import Callable, Dict

from loguru import logger

from ..core.config import PhaseParametersConfig, PhaseScoringParametersConfig, PhaseSearchParametersConfig
from ..environment_client import EnvironmentClient
from ..mcts.phase_registry import phase_registry
from ..tree import ChallengeNode, Tree


class BasePhase:
    """
    A base class for Tree Search implementations that supports both inheritance
    and decorator-based strategy registration.
    Contains common methods and attributes shared by Phase variants.
    """

    def __init__(
        self,
        phase_name: str,
        tree: Tree,
        environment: EnvironmentClient,
        config: dict,
    ) -> None:
        """
        Initialize the BasePhase class.
        This class is not meant to be used directly. It is meant to be subclassed.
        Some configuration parameters need to be present in the subclass:
            - max_depth: Maximum depth for search. Setting this will help stop infinite loops.
            - max_iterations: Maximum number of iterations. Setting this will help stop infinite loops.
            - search_params: Search parameters.
            - num_nodes_per_iteration: Number of nodes to evaluate per iteration, concurrently.
            - convergence_checks: Number of iterations without value changes before stopping.
            - phase_name: Name of the phase to use for decorator-based methods.

        Args:
            phase_name (str): Name of the phase to use for decorator-based methods.
            tree (Tree): The search tree.
            environment (EnvironmentClient): The environment client.
            config (dict): Configuration dictionary loaded from YAML.
        """
        self.phase_name = phase_name
        self.tree = tree
        self.environment = environment

        # set phase parameters
        self.phase_params = PhaseParametersConfig(**config["phase_params"])
        # set search parameters
        self.search_params = PhaseSearchParametersConfig(**config["search_params"])
        # set scoring parameters
        self.scoring_params = PhaseScoringParametersConfig(**config["scoring_params"])

        # flag to indicate if the algorithm has converged
        self.convergence = False
        self.no_change_iterations = 0

        # set of nodes that are being expanded. used to avoid conflicts when selecting nodes
        self.nodes_being_expanded = set()

        timestamp = datetime.now().strftime("%m%d_%H%M")
        experiment_name = f"{timestamp}_{self.phase_name or str(self.__class__)}_{self.phase_params.max_depth}"
        path = os.path.join(os.getcwd(), "experiments", experiment_name)
        os.makedirs(path, exist_ok=True)
        self.path = path

        logger.info(f"Initialized {self.phase_name or str(self.__class__)} with experiment path: {path}")

    def set_resume_state(self, iteration: int) -> None:
        """
        Set the starting iteration for resuming a phase.

        Args:
            iteration: The iteration number to resume from
        """
        self._starting_iteration = iteration
        logger.info(f"Set resume state for {self.phase_name} at iteration {iteration}")

    async def initialize_phase(self) -> None:
        """
        Initializes the phase.
        """
        try:
            strategy_method = self._get_phase_method("initialize_phase")
            await strategy_method(self)
            logger.info(f"Phase {self.phase_name} initialized")
        except NotImplementedError:
            logger.warning(f"No initialize_phase method found for phase {self.phase_name}")

    async def run(self) -> None:
        """
        Runs the search algorithm until convergence based on value changes, using a task
        queue to continuously submit new nodes for execution in a non-blocking manner.
        """
        logger.info(f"Starting {self.phase_name or str(self.__class__)} search algorithm")
        logger.info(f"Max iterations: {self.phase_params.max_iterations}, Max depth: {self.phase_params.max_depth}")
        logger.debug(f"Phase params: {self.phase_params}")
        logger.debug(f"Search params: {self.search_params}")
        logger.debug(f"Scoring params: {self.scoring_params}")
        logger.debug(f"Environment: {self.environment}")

        # Handle resume iteration
        iteration = getattr(self, "_starting_iteration", 0)  # keep track of the number of iterations
        running_tasks = {}  # keep track of the running tasks

        # initialize the phase - skip if resuming from same phase at iteration > 0
        if iteration == 0:
            await self.initialize_phase()
        else:
            logger.info(f"Skipping initialization, resuming from iteration {iteration}")

        try:
            while not self.convergence and iteration < self.phase_params.max_iterations:
                # fill the task queue with new nodes
                await self.fill_task_queue(running_tasks)
                # wait for at least one task to complete before re-evaluating
                # and adding new nodes to running tasks
                if running_tasks:
                    done, pending = await asyncio.wait(
                        running_tasks.values(),
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    logger.debug(f"Tasks completed: {len(done)}, pending: {len(pending)}")

                    # remove completed tasks from running tasks
                    completed_ids = [nid for nid, task in running_tasks.items() if task in done]
                    for nid in completed_ids:
                        del running_tasks[nid]

                    # increment iteration count by the number of completed tasks
                    iteration += len(done)
                else:
                    iteration += 1

                if self.no_change_iterations >= self.phase_params.convergence_checks:
                    logger.info(
                        f"Convergence achieved after {iteration} iterations (no changes for {self.no_change_iterations} iterations)"
                    )
                    self.convergence = True
                else:
                    logger.debug(f"Iteration {iteration}: No change iterations: {self.no_change_iterations}")

                # Log progress every 10 iterations
                if iteration % 10 == 0:
                    logger.info(
                        f"Progress: Iteration {iteration}/{self.phase_params.max_iterations}, Tree size: {len(self.tree.nodes)} nodes"
                    )

                self.save_progress(
                    self.path,
                    f"{self.phase_name}_iteration_{iteration}",
                )

        except asyncio.CancelledError:
            logger.warning("Search cancelled, stopping all tasks")
            for task in running_tasks.values():
                task.cancel()
            await asyncio.gather(
                *running_tasks.values(),
                return_exceptions=True,
            )
            self.save_progress(self.path, f"tree_cancelled_iteration_{iteration}")
            raise

        # wait for all remaining tasks to complete
        if running_tasks:
            logger.info("Waiting for remaining tasks to complete...")
            await asyncio.wait(running_tasks.values())
            logger.debug("All remaining tasks completed")

        logger.info(f"Search completed after {iteration} iterations with {len(self.tree.nodes)} total nodes")
        self.save_progress(
            self.path,
            f"{self.phase_name}_final",
        )

    async def fill_task_queue(
        self,
        running_tasks: Dict[str, asyncio.Task],
    ) -> None:
        """
        Fills the running_tasks queue with new nodes.
        Checks for node conflicts and retries node selection in case of conflicts.

        Args:
            running_tasks (Dict[str, asyncio.Task]): The running tasks.

        Returns:
            None
        """
        while len(running_tasks) < self.phase_params.num_nodes_per_iteration:
            logger.debug(
                f"Task queue status: {len(running_tasks)}/{self.phase_params.num_nodes_per_iteration} tasks running"
            )

            # initialize node selection with retry mechanism
            selected_node = None
            # prevent infinite loops
            attempts = 0
            max_attempts = 10

            while not selected_node and attempts < max_attempts:
                attempts += 1
                candidate = await self.select_node()
                logger.debug(f"Node selection attempt {attempts}: candidate {candidate.id} ({candidate.concepts})")

                # check for node conflicts
                # make sure that the selected node is not a parent of any already running or being expanded nodes
                if await self.check_for_node_conflicts(candidate, running_tasks):
                    selected_node = candidate
                    logger.debug(f"Selected valid node: {selected_node.id}")
                else:
                    logger.debug(f"Node {candidate.id} conflicts with running/expanding nodes, retrying")
                # yield control back to main loop in case of cancellation
                await asyncio.sleep(0)

            # if we couldn't find a valid node after max attempts, wait briefly and continue outer loop
            if not selected_node:
                logger.warning(f"Failed to find eligible node after {max_attempts} attempts, waiting 2 seconds")
                await asyncio.sleep(2)
                continue

            logger.debug(
                f"Creating evaluation task for node {selected_node.id} ({selected_node.concepts}, {selected_node.difficulty})"
            )
            # timeout is now handled internally within evaluate_node_task
            task = asyncio.create_task(self.evaluate_node_task(selected_node))

            running_tasks[selected_node.id] = task

            logger.debug(f"Task queue updated: {len(running_tasks)} tasks now running")

    async def check_for_node_conflicts(
        self,
        candidate_node: ChallengeNode,
        running_tasks: Dict[str, asyncio.Task],
    ) -> bool:
        """
        Check if a node conflicts with any other node in the running or expanding set.

        Args:
            candidate_node (ChallengeNode): The candidate node to check for conflicts.
            running_tasks (Dict[str, asyncio.Task]): The running tasks.

        Returns:
            bool: True if there are no conflicts, False otherwise.
        """
        # get candidate's ID and ancestors
        candidate_and_ancestors = {candidate_node.id} | set(candidate_node.get_node_ancestors_ids())

        # check if any related node is already running or being expanded
        running_conflict = any(nid in running_tasks for nid in candidate_and_ancestors)
        expansion_conflict = any(nid in self.nodes_being_expanded for nid in candidate_and_ancestors)

        return not (running_conflict or expansion_conflict)

    async def evaluate_node_task(
        self,
        node: ChallengeNode,
    ) -> None:
        """
        Function for evaluating a node in a separate task.
        Handles exceptions and cancellation.

        Args:
            node (ChallengeNode): The node to evaluate.

        Returns:
            None
        """
        logger.debug(f"Starting evaluation task for node {node.id} ({node.concepts}, {node.difficulty})")
        try:
            await self.evaluate_node(node, timeout=self.phase_params.task_timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Evaluation timed out for node {node.id} after {self.phase_params.task_timeout} seconds")
            # remove the node from tree and being expanded set if timeout happens
            try:
                self.nodes_being_expanded.discard(node.id)
                logger.info(f"Removed timed-out node {node.id} from task queue")
            except Exception as e:
                logger.warning(f"Error removing timed-out node {node.id}: {e}")
        except asyncio.CancelledError:
            logger.debug(f"Evaluation cancelled for node {node.id}")
            raise
        except Exception as e:
            logger.exception(f"Error evaluating node {node.id} ({node.concepts}): {e}")
        finally:
            logger.debug(f"Evaluation task completed for node {node.id}")

    async def select_node(self) -> ChallengeNode:
        """
        Select a node for evaluation. Uses registered strategy or raises NotImplementedError.
        This method MUST be registered using @phase_registry.register_phase_method('phase_name', 'select_node').
        It defined the logic for selecting a node for evaluation.

        Returns:
            ChallengeNode: The node selected for simulation.
        """
        strategy_method = self._get_phase_method("select_node")
        try:
            return await strategy_method(self)
        except Exception as e:
            logger.exception(f"Error selecting node: {e}")
            raise

    async def _timeout_task(self, timeout: float, node_id: str) -> None:
        """
        Background task that raises TimeoutError after the specified timeout.

        Args:
            timeout (float): The timeout limit in seconds.
            node_id (str): The node ID for logging purposes.

        Raises:
            asyncio.TimeoutError: After the timeout period elapses.
        """
        await asyncio.sleep(timeout)
        logger.warning(f"Timeout triggered for node {node_id} after {timeout} seconds")
        raise asyncio.TimeoutError(f"Operation timed out after {timeout} seconds")

    async def evaluate_node(
        self,
        node: ChallengeNode,
        timeout: float = None,
    ) -> None:
        """
        Evaluate a node. Uses registered strategy or raises NotImplementedError.
        This method MUST be registered using @phase_registry.register_phase_method('phase_name', 'evaluate_node').
        It defined the logic for evaluating a node once it is selected.

        Args:
            node (ChallengeNode): The node to evaluate.
            timeout (float, optional): The timeout limit in seconds.

        Returns:
            None
        """
        strategy_method = self._get_phase_method("evaluate_node")
        timeout_task = None
        evaluation_task = None

        try:
            logger.debug(f"Starting evaluation of node {node.id} ({node.concepts}, {node.difficulty})")

            # Create the main evaluation task
            async def _run_evaluation():
                # evaluate node
                evaluation_results = await strategy_method(self, node)
                logger.debug(
                    f"Node {node.id} evaluation completed with success: {evaluation_results.get('success', False)}"
                )

                # update node data
                data_trail = evaluation_results.get("data_trail", [])
                if data_trail and len(data_trail) > 0:
                    self.update_node_data(node, evaluation_results)
                else:
                    logger.error(f"Empty data trail for node {node.id}. removing node from tree")
                    self.nodes_being_expanded.discard(node.id)
                    if node.depth > 1 and not node.children:  # don't remove root node or nodes with children
                        self.tree.remove_node(node)
                    # return early to prevent further processing of removed node
                    return None

                # calculate node value
                previous_node_value = node.value
                node_value = self.calculate_node_value(
                    results=evaluation_results,
                    difficulty_level=node.difficulty,
                )

                # backpropagate node value
                self.backpropagate_node_value(node, node_value)

                # yield control back to main loop in case of cancellation
                await asyncio.sleep(0)

                # Check for convergence
                value_delta = abs(node.value - previous_node_value)
                if value_delta <= self.phase_params.value_delta_threshold:
                    self.no_change_iterations += 1
                    logger.debug(
                        f"Node {node.id} value change {value_delta:.4f} below threshold, no_change_iterations: {self.no_change_iterations}"
                    )
                else:
                    self.no_change_iterations = 0
                    logger.debug(f"Node {node.id} value changed by {value_delta:.4f}, resetting no_change_iterations")

                # expand node
                await self.expand_node(node)
                try:
                    self.nodes_being_expanded.discard(node.id)
                except KeyError:
                    logger.warning(f"Node {node.id} not found in nodes_being_expanded set")

                return evaluation_results

            # Create tasks for evaluation and timeout
            evaluation_task = asyncio.create_task(_run_evaluation())

            if timeout is not None:
                timeout_task = asyncio.create_task(self._timeout_task(timeout, node.id))

                # Race the evaluation against the timeout
                done, pending = await asyncio.wait([evaluation_task, timeout_task], return_when=asyncio.FIRST_COMPLETED)

                # Cancel any pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # Check which task completed first
                completed_task = done.pop()
                if completed_task == timeout_task:
                    # Timeout occurred, get the exception
                    await completed_task  # This will raise TimeoutError
                else:
                    # Evaluation completed normally, get the result
                    await completed_task
            else:
                # No timeout specified, just run the evaluation
                await evaluation_task

        except Exception as e:
            logger.error(f"Error during evaluation of node {node.id} ({node.concepts}): {e}")

            # Clean up tasks if they exist
            if evaluation_task and not evaluation_task.done():
                evaluation_task.cancel()
                try:
                    await evaluation_task
                except asyncio.CancelledError:
                    pass

            if timeout_task and not timeout_task.done():
                timeout_task.cancel()
                try:
                    await timeout_task
                except asyncio.CancelledError:
                    pass

            self.nodes_being_expanded.discard(node.id)
            if node.depth > 1 and not node.children:  # don't remove root node or nodes with children
                self.tree.remove_node(node)

            raise

    def update_node_data(
        self,
        node: ChallengeNode,
        results: Dict,
    ) -> None:
        """
        Updates the node with the results from the challenge simulation.

        Args:
            node (ChallengeNode): The node to update.
            results (Dict): The results from the challenge simulation.
        """
        # extract data from results based on the new data structure
        data_trail = results["data_trail"]

        # get the first successful attempt or the last attempt
        successful_attempt = next((dt for dt in data_trail if dt.get("success")), data_trail[-1])
        node.challenge_description = successful_attempt.get("problem_statement", "")
        logger.debug(f"Updated node {node.id} with challenge data from {len(data_trail)} attempts")

    def calculate_node_value(
        self,
        results: Dict,
        **kwargs,
    ) -> float:
        """
        Calculate node value. Uses registered strategy or raises NotImplementedError.
        This method MUST be registered using @phase_registry.register_phase_method('phase_name', 'calculate_node_value').
        It defined the logic for calculating the value of a node based on the results of the challenge simulation.
        This function is not async. It is meant to be blocking.

        Args:
            results (Dict): The results from the challenge simulation.
            **kwargs: Additional keyword arguments.

        Returns:
            float: The calculated score.
        """
        try:
            strategy_method = self._get_phase_method("calculate_node_value")

            return strategy_method(self, results, **kwargs)
        except Exception as e:
            logger.exception(f"Error calculating node value: {e}")
            raise

    def backpropagate_node_value(
        self,
        node: ChallengeNode,
        reward: float,
    ) -> None:
        """
        Backpropagate node value. Uses registered strategy or raises NotImplementedError.
        This method MUST be registered using @phase_registry.register_phase_method('phase_name', 'backpropagate_node_value').
        It defined the logic for backpropagating the value of a node up the tree based on the results of the challenge simulation.
        This function is not async. It is meant to be blocking.

        Args:
            node (ChallengeNode): The node where backpropagation starts.
            reward (float): The reward to backpropagate.
        """
        try:
            strategy_method = self._get_phase_method("backpropagate_node_value")
            strategy_method(self, node, reward)
        except Exception as e:
            logger.exception(f"Error backpropagating node value: {e}")
            raise

    async def expand_node(
        self,
        node: ChallengeNode,
    ) -> None:
        """
        Expand a node. Uses registered strategy or raises NotImplementedError.
        This method MUST be registered using @phase_registry.register_phase_method('phase_name', 'expand_node').
        It defined the logic for expanding a node.

        Args:
            node (ChallengeNode): The node to expand.

        Returns:
            None
        """
        strategy_method = self._get_phase_method("expand_node")

        node_and_ancestors = {node.id} | set(node.get_node_ancestors_ids())

        # If any of these nodes are being expanded elsewhere, skip expansion
        if any(nid in self.nodes_being_expanded for nid in node_and_ancestors):
            logger.debug(f"Skipping expansion of node {node.id} - ancestor already being expanded")
            return

        self.nodes_being_expanded.add(node.id)

        try:
            await strategy_method(self, node)
        except Exception as e:
            logger.exception(f"Error expanding node {node.id} ({node.concepts}): {e}")
            raise

    def _get_phase_method(
        self,
        method_name: str,
    ) -> Callable:
        """
        Get a strategy method, either from registry or raise an error.

        Args:
            method_name (str): Name of the method to get

        Returns:
            Callable: The strategy method

        Raises:
            NotImplementedError: If no strategy is found for the method
        """
        if self.phase_name:
            phase_method = phase_registry.get_phase_method(self.phase_name, method_name)
            if phase_method:
                return phase_method

        raise NotImplementedError(
            f"No strategy found for {method_name}. "
            f"Either implement it in a subclass or register it using "
            f"@phase_registry.register_phase_method('{self.phase_name}', '{method_name}')"
        )

    def save_progress(
        self,
        path: str,
        iteration: str,
    ) -> None:
        """
        Saves the current state of the tree and its visualization.

        Args:
            path (str): The directory path where the files will be saved.
            iteration (str): The current iteration number or 'final'.
        """
        logger.debug(f"Saving progress for phase {self.phase_name} iteration {iteration}")

        file_prefix = f"{self.phase_name}_tree_{iteration}"

        self.tree.save_tree(file_name=os.path.join(path, file_prefix))
        self.tree.visualize_tree(file_name=os.path.join(path, file_prefix))
