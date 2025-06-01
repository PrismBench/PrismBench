import random
from typing import TYPE_CHECKING, Dict

from loguru import logger

from ..mcts.phase_registry import phase_registry
from ..tree import ChallengeNode

if TYPE_CHECKING:
    from ..mcts.base_phase import BasePhase


@phase_registry.register_phase_method("phase_2", "initialize_phase")
async def initialize_phase(phase: "BasePhase") -> None:
    """
    Updates the values of the nodes in the tree.
    """
    for node in phase.tree.nodes:
        if node.run_results:
            node.value = phase.calculate_node_value(results=node.run_results[-1], difficulty_level=node.difficulty)
        else:
            node.value = 0.0
    return phase


@phase_registry.register_phase_method("phase_2", "select_node")
async def select_node(self: "BasePhase") -> ChallengeNode:
    """
    Selects a node to explore based on a probability distribution inversely proportional
    to their values to favor less-explored nodes.

    Args:
        self (BasePhase): The BasePhase instance

    Returns:
        ChallengeNode: The node selected for evaluation.
    """

    scores = [(node.value + 1e-3) for node in self.tree.nodes]

    total_score = sum(scores)
    if total_score == 0:
        # if all scores are zero, select randomly
        probabilities = [1 / len(scores)] * len(scores)
    else:
        probabilities = [(score) / total_score for score in scores]

    if random.random() < self.phase_params.exploration_probability:
        node = random.choice(self.tree.nodes)
        logger.debug(f"Random exploration: selected node {node.id} ({node.concepts}, {node.difficulty})")
    else:
        node = random.choices(self.tree.nodes, weights=probabilities)[0]
        logger.debug(f"Probability-based selection: selected node {node.id} ({node.concepts}, {node.difficulty})")
    # once a node is selected, traverse it until a leaf node is reached
    while node.children:
        # random probability of selecting a child node
        if random.random() < self.phase_params.exploration_probability:
            node = random.choice(node.children)
            logger.debug(f"Random child exploration: selected {node.id} ({node.concepts}, {node.difficulty})")
        # otherwise, select the best child node based on UCB1
        else:
            node = max(node.children, key=lambda n: n.ucb1())
            logger.debug(f"UCB1 child selection: selected {node.id} ({node.concepts}, {node.difficulty})")

    return node


@phase_registry.register_phase_method("phase_2", "evaluate_node")
async def evaluate_node(
    self: "BasePhase",
    node: ChallengeNode,
) -> Dict:
    """
    Evaluate a node.

    Args:
        self (BasePhase): The BasePhase instance
        node (ChallengeNode): The node to evaluate

    Returns:
        Dict: The evaluation results
    """
    logger.debug(f"Running challenge for node {node.id} ({node.concepts}, {node.difficulty})")

    # Call the environment service asynchronously
    evaluation_results = await self.environment.run_challenge(
        concept=node.concepts,
        difficulty_level=node.difficulty,
        max_attempts=self.search_params.max_attempts,
    )

    node.run_results.append(evaluation_results)

    success = evaluation_results.get("success", False)
    data_trail_length = len(evaluation_results.get("data_trail", []))
    logger.debug(f"Challenge completed for node {node.id}: success={success}, attempts={data_trail_length}")

    return evaluation_results


@phase_registry.register_phase_method("phase_2", "calculate_node_value")
def calculate_node_value(
    self: "BasePhase",
    results: Dict,
    difficulty_level: str,
    **kwargs,
) -> float:
    """
    Calculates how challenging a problem was based on:
    - Success rate
    - Number of attempts needed
    - Whether it needed fixes
    Higher score means more challenging.

    Args:
        results (Dict): The results from the challenge simulation.

    Returns:
        float: The challenge score.
    """
    # Extract metrics from data trail
    try:
        data_trail = results.get("data_trail", [])

        # Calculate total tests across all attempts
        total_tests = 0
        success_count = 0

        for dt in data_trail:
            attempt_tests = (
                dt.get("tests_passed_num", 0) + dt.get("tests_failed_num", 0) + dt.get("tests_errored_num", 0)
            )
            total_tests += attempt_tests
            if dt.get("success"):
                success_count += dt.get("tests_passed_num", 0)

        # Invert success rate - higher means more challenging
        if total_tests > 0:
            success_rate = success_count / total_tests
        else:
            success_rate = 0
        challenge_from_success = 1 - success_rate

        # More attempts means more challenging
        successful_attempts = [dt for dt in data_trail if dt.get("success")]
        attempts = len(data_trail) if not successful_attempts else data_trail.index(successful_attempts[0]) + 1
        attempt_factor = min(attempts / 3, 1.0)

        # Needing fixes means more challenging
        fixer_factor = 0
        if data_trail and data_trail[-1].get("success") and data_trail[-1].get("fixed_by_problem_fixer"):
            fixer_factor = 1.0

        # Weighted combination
        challenge_score = (
            challenge_from_success * 0.5  # Weight success rate highest
            + attempt_factor * 0.3  # Weight attempts next
            + fixer_factor * 0.2  # Weight fixes least
        )

        return challenge_score
    except Exception as e:
        logger.exception(f"Error calculating node value: {e}")
        return 0.0


@phase_registry.register_phase_method("phase_2", "backpropagate_node_value")
def backpropagate_node_value(
    self: "BasePhase",
    node: ChallengeNode,
    reward: float,
) -> None:
    """
    Backpropagates the reward up the tree using a discount factor.

    Args:
        node (ChallengeNode): The node where backpropagation starts.
        reward (float): The reward to propagate.
    """
    gamma = self.search_params.discount_factor
    learning_rate = self.search_params.learning_rate

    # update the node value
    old_value = node.value
    node.update_node_score(learning_rate, reward)
    logger.debug(f"Updated node {node.id} value: {old_value:.3f} -> {node.value:.3f} (reward: {reward:.3f})")

    # if the node has no parents, return
    if not node.parents:
        return

    # backpropagate the reward up the tree
    for parent_node in node.parents:
        discounted_reward = reward * gamma
        self.backpropagate_node_value(
            parent_node,
            discounted_reward,
        )


@phase_registry.register_phase_method("phase_2", "expand_node")
async def expand_node(
    self: "BasePhase",
    node: ChallengeNode,
) -> None:
    """
    Attempts to expand the node repeatedly while it meets the criteria.

    Args:
        node (ChallengeNode): The node to attempt expansion on.
    """

    current_node = node
    expansion_count = 0

    while (
        current_node.value >= self.phase_params.performance_threshold
        and current_node.depth <= self.phase_params.max_depth
    ):
        # `BasePhase.expand_node` has already added *current_node.id* to
        # `self.nodes_being_expanded` before delegating here. Treating the
        # current node as a conflict would therefore stop all expansion.
        # We only want to guard against *other* nodes/ancestors that are
        # currently being expanded elsewhere.
        ancestors = set(current_node.get_node_ancestors_ids())
        if any(nid in self.nodes_being_expanded for nid in ancestors):
            logger.debug(f"Stopping expansion of node {current_node.id} - ancestor being expanded elsewhere")
            break

        if random.random() < self.phase_params.exploration_probability:
            logger.debug(f"Expanding node {current_node.id} by adding new concepts")
            second_node = await self.select_node()
            expanded_node = self.tree.add_node([current_node, second_node], phase=2)
        else:
            logger.debug(f"Expanding node {current_node.id} by increasing difficulty")
            expanded_node = self.tree.add_node([current_node], phase=2)

        expansion_count += 1

        if expanded_node.visits == 0:
            logger.info(
                f"Created new node {expanded_node.id} ({expanded_node.concepts}, {expanded_node.difficulty}) from node {current_node.id}"
            )
            # process the expanded node
            await self.evaluate_node(expanded_node)

            # check if the node still exists in the tree after evaluation
            # if it was removed due to empty data trail, don't continue processing
            if expanded_node not in self.tree.nodes:
                logger.debug(f"Node {expanded_node.id} was removed during evaluation, stopping expansion")
                break

            # update current_node to continue expansion from the new node
            current_node = expanded_node
        else:
            logger.debug(
                f"Reusing existing node {expanded_node.id} ({expanded_node.concepts}, {expanded_node.difficulty})"
            )
            # for existing nodes, we can choose to continue expansion or stop
            # if the existing node has a good value, continue from it
            if expanded_node.value >= self.phase_params.performance_threshold:
                current_node = expanded_node
            else:
                # stop expansion if the existing node doesn't meet threshold
                logger.debug(
                    f"Stopping expansion - existing node {expanded_node.id} value {expanded_node.value:.3f} below threshold {self.phase_params.performance_threshold}"
                )
                break

    if expansion_count > 0:
        logger.debug(f"Expansion completed for node {node.id}: {expansion_count} nodes processed")
    else:
        logger.debug(f"No expansion performed for node {node.id} (value: {node.value:.3f}, depth: {node.depth})")
