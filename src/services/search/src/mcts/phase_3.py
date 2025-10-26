import random
from typing import TYPE_CHECKING, Dict

from loguru import logger

from ..mcts.phase_registry import phase_registry
from ..tree import ChallengeNode

if TYPE_CHECKING:
    from ..mcts.base_phase import BasePhase


@phase_registry.register_phase_method("phase_3", "initialize_phase")
async def initialize_phase(phase: "BasePhase") -> None:
    """
    Updates the values of the nodes in the tree and creates phase 3 nodes.
    This method is called at the beginning of phase 3.

    Args:
        phase (BasePhase): The phase instance

    Returns:
        None
    """
    for node in phase.tree.nodes:
        if node.phase == 2 and node.value > phase.phase_params.node_selection_threshold:
            node.phase_2_value = node.value
            for i in range(phase.phase_params.variations_per_concept):
                phase.tree.add_node(
                    parent_nodes=[node],
                    concepts=node.concepts,
                    difficulty=node.difficulty,
                    phase=3,
                )

    return phase


@phase_registry.register_phase_method("phase_3", "select_node")
async def select_node(self: "BasePhase") -> ChallengeNode:
    """
    Selects a node to explore based on a probability distribution inversely proportional
    to their values to favor less-explored nodes.

    Args:
        self (BasePhase): The BasePhase instance

    Returns:
        ChallengeNode: The node selected for evaluation.
    """

    nodes_to_select = [node for node in self.tree.nodes if node.phase == 3]
    scores = [(node.value + 1e-3) for node in nodes_to_select]

    total_score = sum(scores)
    if total_score == 0:
        # if all scores are zero, select randomly
        probabilities = [1 / len(scores)] * len(scores)
    else:
        probabilities = [(score) / total_score for score in scores]

    if random.random() < self.phase_params.exploration_probability:
        node = random.choice(nodes_to_select)
        logger.debug(f"Random exploration: selected node {node.id} ({node.concepts}, {node.difficulty})")
    else:
        node = random.choices(nodes_to_select, weights=probabilities)[0]
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


@phase_registry.register_phase_method("phase_3", "evaluate_node")
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

    previous_problems = []
    for parent_node in node.parents:
        for child_node in parent_node.children:
            previous_problems.append(
                child_node.run_results[-1].get("problem_statement", "") if child_node.run_results else ""
            )

    # Call the environment service asynchronously
    evaluation_results = await self.environment.run_challenge(
        concept=node.concepts,
        difficulty_level=node.difficulty,
        max_attempts=self.search_params.max_attempts,
        previous_problems=previous_problems,
    )

    node.run_results.append(evaluation_results)

    success = evaluation_results.get("success", False)
    data_trail_length = len(evaluation_results.get("data_trail", []))
    logger.debug(f"Challenge completed for node {node.id}: success={success}, attempts={data_trail_length}")

    return evaluation_results


@phase_registry.register_phase_method("phase_3", "calculate_node_value")
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


@phase_registry.register_phase_method("phase_3", "backpropagate_node_value")
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


@phase_registry.register_phase_method("phase_3", "expand_node")
async def expand_node(
    self: "BasePhase",
    node: ChallengeNode,
) -> None:
    """
    Attempts to expand the node repeatedly while it meets the criteria.
    Phase 3 does not expand nodes. It only runs the challenges and backpropagates the value.

    Args:
        node (ChallengeNode): The node to attempt expansion on.
    """

    pass
