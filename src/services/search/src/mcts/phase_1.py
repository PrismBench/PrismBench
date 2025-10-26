import random
from typing import TYPE_CHECKING, Dict

from loguru import logger

from ..mcts.phase_registry import phase_registry
from ..tree import ChallengeNode

if TYPE_CHECKING:
    from ..mcts.base_phase import BasePhase


@phase_registry.register_phase_method("phase_1", "select_node")
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
    # check if there are any nodes with value 0 (unexplored)
    zero_value_nodes = [node for node in self.tree.nodes if node.value == 0]
    if zero_value_nodes and len(zero_value_nodes) > 20:
        # if there are unexplored nodes, prioritize them exclusively
        # equal probability among all zero-value nodes
        probabilities = []
        for node in self.tree.nodes:
            if node.value == 0:
                probabilities.append(1.0 / len(zero_value_nodes))
            else:
                probabilities.append(0.0)
        logger.debug(f"Prioritizing {len(zero_value_nodes)} unexplored nodes (value=0)")
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


@phase_registry.register_phase_method("phase_1", "evaluate_node")
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


@phase_registry.register_phase_method("phase_1", "calculate_node_value")
def calculate_node_value(
    self: "BasePhase",
    results: Dict,
    difficulty_level: str,
) -> float:
    """
    Calculates a normalized score for a challenge result.

    The score is influenced by the success of the challenge, the number of tests passed,
    penalties for failures, errors, attempts, and whether the problem was fixed by a fixer.

    Args:
        result (Dict): The results from the challenge simulation.
        difficulty_level (str): The difficulty level of the challenge.

    Returns:
        float: The normalized score between 0 and 1.
    """
    difficulty_weights = {
        "very easy": 1,
        "easy": 1.5,
        "medium": 2,
        "hard": 2.5,
        "very hard": 3,
    }
    base_score = (10 if results.get("success") else 0) * difficulty_weights.get(difficulty_level, 1)

    # Extract metrics from data trail
    data_trail = results.get("data_trail", [])

    # Sum up all test results across all attempts
    num_passed = sum(dt.get("tests_passed_num", 0) for dt in data_trail)
    num_failed = sum(dt.get("tests_failed_num", 0) for dt in data_trail)
    num_errors = sum(dt.get("tests_errored_num", 0) for dt in data_trail)

    # Count successful attempts
    successful_attempts = [dt for dt in data_trail if dt.get("success")]
    attempts_till_success = len(data_trail) if not successful_attempts else data_trail.index(successful_attempts[0]) + 1

    # Check if fixed by problem fixer (last attempt was successful and marked as fixed)
    fixed_by_problem_fixer = False
    if data_trail and data_trail[-1].get("success") and data_trail[-1].get("fixed_by_problem_fixer"):
        fixed_by_problem_fixer = True

    # Penalties for failures, errors, and attempts
    failure_penalty = num_failed * self.scoring_params.penalty_per_failure
    error_penalty = num_errors * self.scoring_params.penalty_per_error
    attempt_penalty = (attempts_till_success - 1) * self.scoring_params.penalty_per_attempt
    fixer_penalty = self.scoring_params.fixed_by_problem_fixer_penalty if fixed_by_problem_fixer else 0

    raw_score = base_score + num_passed - (failure_penalty + error_penalty + attempt_penalty + fixer_penalty)
    raw_score = max(raw_score, 0)  # Ensure the score is not negative

    # Normalize the score between 0 and 1
    max_base_score = 10 * max(difficulty_weights.values())
    max_raw_score = max_base_score + self.scoring_params.max_num_passed
    normalized_score = raw_score / max_raw_score

    logger.debug(
        f"Score calculation: base={base_score:.1f}, passed={num_passed}, penalties={failure_penalty + error_penalty + attempt_penalty + fixer_penalty:.1f}, normalized={normalized_score:.3f}"
    )

    return normalized_score


@phase_registry.register_phase_method("phase_1", "backpropagate_node_value")
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


@phase_registry.register_phase_method("phase_1", "expand_node")
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
            expanded_node = self.tree.add_node([current_node, second_node])
        else:
            logger.debug(f"Expanding node {current_node.id} by increasing difficulty")
            expanded_node = self.tree.add_node([current_node])

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
