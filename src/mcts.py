import math
import os
import random
from datetime import datetime
from typing import Dict, Optional

import yaml
from loguru import logger

from environment import CodingChallengeEnvironment, EnhancedCodingChallengeEnvironment
from node import ChallengeNode
from tree import Tree

# Load configurations from YAML file as global constants

with open(
    os.path.join(
        os.getcwd(),
        "configs.yml",
    ),
    "r",
) as f:
    configs = yaml.safe_load(f)

# Global constants
MAX_ATTEMPTS = configs["max_attempts"]
DISCOUNT_FACTOR = configs["discount_factor"]

# Phase 1 configurations
PHASE_ONE_PERFORMANCE_THRESHOLD = configs["phase1"]["performance_threshold"]
PHASE_ONE_VALUE_DELTA_THRESHOLD = configs["phase1"]["value_delta_threshold"]
PHASE_ONE_CONVERGENCE_CHECKS = configs["phase1"]["convergence_checks"]
PHASE_ONE_EXPLORATION_PROBABILITY = configs["phase1"]["exploration_probability"]

# Phase 1 scoring parameters
PENALTY_PER_FAILURE = configs["phase1"]["scoring"]["penalty_per_failure"]
PENALTY_PER_ERROR = configs["phase1"]["scoring"]["penalty_per_error"]
PENALTY_PER_ATTEMPT = configs["phase1"]["scoring"]["penalty_per_attempt"]
FIXED_BY_PROBLEM_FIXER_PENALTY = configs["phase1"]["scoring"][
    "fixed_by_problem_fixer_penalty"
]
MAX_NUM_PASSED = configs["phase1"]["scoring"]["max_num_passed"]

# Phase 2 configurations
PHASE_TWO_VALUE_DELTA_THRESHOLD = configs["phase2"]["value_delta_threshold"]
PHASE_TWO_CONVERGENCE_CHECKS = configs["phase2"]["convergence_checks"]
CHALLENGE_THRESHOLD = configs["phase2"]["challenge_threshold"]
EXPLORATION_WEIGHT = configs["phase2"]["exploration_weight"]
PHASE_TWO_EXPLORATION_PROBABILITY = configs["phase2"]["exploration_probability"]

# Phase 3 configurations
VARIAITONS_PER_CONCEPT = configs["phase3"]["variations_per_concept"]
NODE_SELECTION_THRESHOLD = configs["phase3"]["node_selection_threshold"]


class BaseMCTS:
    """
    A base class for Monte Carlo Tree Search implementations.
    Contains common methods and attributes shared by MCTS variants.
    """

    def __init__(
        self,
        environment: CodingChallengeEnvironment,
        tree: Tree,
        max_depth: int,
        iterations: int,
    ):
        self.environment = environment
        self.tree = tree
        self.max_depth = max_depth
        self.iterations = iterations

    def select_node(self) -> ChallengeNode:
        """
        Selects a node to explore based on a probability distribution inversely proportional
        to their values to favor less-explored nodes.

        Returns:
            ChallengeNode: The node selected for simulation.
        """
        scores = [node.value for node in self.tree.nodes]

        # At the start, select a node randomly as all have zero scores
        if all(value == 0 for value in scores):
            node = random.choice(self.tree.nodes)
        else:
            inverse_scores = [1 / (score + 1e-10) for score in scores]
            total_inverse_score = sum(inverse_scores)
            probabilities = [score / total_inverse_score for score in inverse_scores]
            node = random.choices(self.tree.nodes, probabilities)[0]

        # Traverse to a leaf node
        while node.children:
            if self.should_explore():
                node = random.choice(node.children)
                logger.debug(f"Randomly selected child node: {node.concepts}")
            else:
                node = self.select_best_child(node)
                logger.debug(f"Selected child node using strategy: {node.concepts}")
        return node

    def should_explore(self) -> bool:
        """
        Determines whether to explore randomly or exploit based on the exploration probability.

        Returns:
            bool: True if exploring, False otherwise.
        """
        return random.random() < self.exploration_probability

    def select_best_child(
        self,
        node: ChallengeNode,
    ) -> ChallengeNode:
        """
        Selects the best child node based on UCB1 or other criteria.

        Args:
            node (ChallengeNode): The parent node.

        Returns:
            ChallengeNode: The selected child node.
        """
        return max(node.children, key=lambda n: n.ucb1())

    def simulate(
        self,
        node: ChallengeNode,
    ) -> float:
        """
        Simulates the execution of a node by running a coding challenge and calculates the score.

        Args:
            node (ChallengeNode): The node to simulate.

        Returns:
            float: The normalized score obtained from the simulation.
        """
        logger.debug(
            f"Simulating node: Difficulty={node.difficulty}, Concepts={node.concepts}"
        )
        challenge_results = self.environment.run_challenge(
            concept=node.concepts,
            difficulty_level=node.difficulty,
            max_attempts=MAX_ATTEMPTS,
        )
        self.update_node_data(node, challenge_results)
        score = self.calculate_score(
            challenge_results,
            node.difficulty,
        )  # different for each phase
        node.run_results.append(challenge_results)
        logger.debug(f"Simulation completed with score: {score:.2f}")
        return score

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
        node.challenge_description = results.get("problem_statement", "")
        data_trail = results.get("data_trail", {})
        for attempt_num, attempt_details in data_trail.items():
            for field in ["problem_statement", "solution_code", "test_cases"]:
                data = attempt_details.get(field, [])
                getattr(node, field).setdefault(attempt_num, []).append(data)

    def backpropagate(
        self,
        node: ChallengeNode,
        reward: float,
        gamma: float = DISCOUNT_FACTOR,
    ) -> None:
        """
        Backpropagates the reward up the tree using a discount factor.

        Args:
            node (ChallengeNode): The node where backpropagation starts.
            reward (float): The reward to propagate.
            gamma (float): The discount factor applied at each step.
        """
        node.update_node_score(reward)
        for parent_node in node.parents or []:
            discounted_reward = reward * gamma
            self.backpropagate(
                parent_node,
                discounted_reward,
                gamma,
            )

    def save_progress(self, path: str, iteration: str) -> None:
        """
        Saves the current state of the tree and its visualization.

        Args:
            path (str): The directory path where the files will be saved.
            iteration (str): The current iteration number or 'final'.
        """
        self.tree.save_tree(file_name=os.path.join(path, f"tree_{iteration}"))
        self.tree.visualize_tree(file_name=os.path.join(path, f"tree_{iteration}"))


class MCTS(BaseMCTS):
    def __init__(
        self,
        environment: CodingChallengeEnvironment,
        tree: Tree,
        max_depth: int = 10,
        iterations: int = 100,
    ) -> None:
        super().__init__(environment, tree, max_depth, iterations)
        self.performance_threshold = PHASE_ONE_PERFORMANCE_THRESHOLD
        self.convergence_threshold = PHASE_ONE_VALUE_DELTA_THRESHOLD
        self.convergence_checks = PHASE_ONE_CONVERGENCE_CHECKS
        self.exploration_probability = PHASE_ONE_EXPLORATION_PROBABILITY

    def run(self) -> None:
        """
        Runs the MCTS algorithm until convergence based on value changes.

        The algorithm iteratively selects nodes, simulates them, and backpropagates the results.
        It expands nodes when certain criteria are met and stops when the value changes across
        iterations fall below a specified threshold for a number of consecutive checks.
        """
        logger.info("Starting MCTS Phase 1 - run until convergence")
        timestamp = datetime.now().strftime("%m%d_%H%M")
        experiment_name = f"{timestamp}_PHASE_ONE_{self.max_depth}"
        path = os.path.join(os.getcwd(), "experiments", experiment_name)
        os.makedirs(path, exist_ok=True)

        self.no_change_iterations = 0
        iteration = 0

        while True:
            iteration += 1
            logger.debug(f"Iteration {iteration}")
            try:
                node = self.select_node()
                prev_value = node.value
                reward = self.simulate(node)
                self.backpropagate(node, reward)

                value_delta = abs(node.value - prev_value)
                logger.debug(f"Value delta for node {node.concepts}: {value_delta:.4f}")

                # Check convergence criterion
                if value_delta < self.convergence_threshold:
                    self.no_change_iterations += 1
                    if self.no_change_iterations >= self.convergence_checks:
                        logger.info("Convergence achieved based on value changes")
                        break
                else:
                    self.no_change_iterations = 0

                # Attempt to expand node if criteria met
                self.attempt_node_expansion(node)

                if iteration % 10 == 0:
                    self.save_progress(path, iteration)
            except Exception as e:
                logger.exception(f"An error occurred during iteration {iteration}: {e}")
                continue

        logger.info("MCTS run completed")
        self.save_progress(path, "final")

    def attempt_node_expansion(self, node: ChallengeNode) -> None:
        """
        Attempts to expand the node repeatedly while it meets the criteria.

        Args:
            node (ChallengeNode): The node to attempt expansion on.
        """
        while self.should_expand_node(node):
            node = self.expand_node(node)
            prev_value = node.value
            reward = self.simulate(node)
            self.backpropagate(node, reward)

            value_delta = abs(node.value - prev_value)
            logger.debug(f"Value delta for node {node.concepts}: {value_delta:.4f}")

            # Check convergence during expansion
            if value_delta < self.convergence_threshold:
                self.no_change_iterations += 1
                if self.no_change_iterations >= self.convergence_checks:
                    logger.info("Convergence achieved during expansion")
                    break
            else:
                self.no_change_iterations = 0

    def should_expand_node(self, node: ChallengeNode) -> bool:
        """
        Determines whether a node should be expanded based on its value and depth.

        Args:
            node (ChallengeNode): The node to check.

        Returns:
            bool: True if the node should be expanded, False otherwise.
        """
        return node.value >= self.performance_threshold and node.depth <= self.max_depth

    def expand_node(self, node: ChallengeNode) -> ChallengeNode:
        """
        Expands a node by creating a new child node.

        The expansion can be in two ways:
        - By combining the current node with another node to introduce new concepts.
        - By increasing the difficulty level of the current node.

        Args:
            node (ChallengeNode): The node to expand.

        Returns:
            ChallengeNode: The newly created child node.
        """
        if random.random() < self.exploration_probability:
            logger.info("Expanding node by adding new concepts")
            second_node = self.select_node()
            new_node = self.tree.add_node([node, second_node])
        else:
            logger.info("Expanding node by increasing difficulty")
            new_node = self.tree.add_node([node])
        return new_node

    def calculate_score(self, result: Dict, difficulty_level: str) -> float:
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
        base_score = (10 if result.get("success") else 0) * difficulty_weights.get(
            difficulty_level, 1
        )

        num_passed = int(result.get("cumulative_tests_passed", 0))
        num_failed = int(result.get("cumulative_tests_failed", 0))
        num_errors = int(result.get("cumulative_tests_errored", 0))

        # Penalties for failures, errors, and attempts
        failure_penalty = num_failed * PENALTY_PER_FAILURE
        error_penalty = num_errors * PENALTY_PER_ERROR
        attempts = result.get("attempts_till_success", 1)
        attempt_penalty = (attempts - 1) * PENALTY_PER_ATTEMPT
        fixer_penalty = (
            FIXED_BY_PROBLEM_FIXER_PENALTY
            if result.get("fixed_by_problem_fixer")
            else 0
        )

        raw_score = (
            base_score
            + num_passed
            - (failure_penalty + error_penalty + attempt_penalty + fixer_penalty)
        )
        raw_score = max(raw_score, 0)  # Ensure the score is not negative

        # Normalize the score between 0 and 1
        max_base_score = 10 * max(difficulty_weights.values())
        max_raw_score = max_base_score + MAX_NUM_PASSED
        normalized_score = raw_score / max_raw_score
        logger.debug(f"Calculated normalized score: {normalized_score:.2f}")
        return normalized_score


class ConceptMCTS(BaseMCTS):
    """
    Monte Carlo Tree Search implementation focusing on discovering challenging concept combinations.
    Inherits common functionality from BaseMCTS.
    """

    def __init__(
        self,
        environment: CodingChallengeEnvironment,
        tree: Tree,
        max_depth: int = 10,
        iterations: int = 100,
    ):
        super().__init__(environment, tree, max_depth, iterations)
        self.exploration_weight = EXPLORATION_WEIGHT
        self.challenge_threshold = CHALLENGE_THRESHOLD
        self.exploration_probability = PHASE_TWO_EXPLORATION_PROBABILITY
        self.value_delta_threshold = PHASE_TWO_VALUE_DELTA_THRESHOLD
        self.convergence_checks = PHASE_ONE_CONVERGENCE_CHECKS
        self.challenging_combinations = {}

    def run(self) -> Dict[tuple, Dict]:
        """
        Runs the ConceptMCTS algorithm to find challenging concept combinations.
        The algorithm iteratively selects nodes, simulates them, and backpropagates the results.
        It expands nodes focusing on challenging combinations and stops when convergence is achieved.

        Returns:
            Dict[tuple, Dict]: A dictionary of challenging concept combinations found.
        """
        logger.info("Starting Concept Challenge MCTS")
        timestamp = datetime.now().strftime("%m%d_%H%M")
        experiment_name = f"{timestamp}_PHASE_TWO_{self.max_depth}"
        path = os.path.join(os.getcwd(), "experiments", experiment_name)
        os.makedirs(path, exist_ok=True)

        # Convergence parameters
        value_delta_threshold = self.value_delta_threshold
        convergence_checks = self.convergence_checks
        no_change_iterations = 0

        iteration = 0
        while True:
            iteration += 1
            try:
                node = self.select_node()

                if not node.run_results:
                    prev_value = node.value
                    score = self.simulate(node)
                    self.backpropagate(node, score)
                    node.phase = 2
                    self.tree.phase_markers[node] = 2
                    value_delta = abs(node.value - prev_value)
                    logger.debug(
                        f"Value delta for node {node.concepts}: {value_delta:.4f}"
                    )
                else:
                    prev_value = node.value
                    new_node = self.expand_node(node)
                    if new_node:
                        score = self.simulate(new_node)
                        self.backpropagate(new_node, score)
                        value_delta = abs(new_node.value - prev_value)
                        logger.debug(
                            f"Value delta for new node {new_node.concepts}: {value_delta:.4f}"
                        )
                    else:
                        value_delta = 0

                # Check convergence criterion
                if value_delta < value_delta_threshold:
                    no_change_iterations += 1
                    if no_change_iterations >= convergence_checks:
                        logger.info("Convergence achieved based on value changes")
                        break
                else:
                    no_change_iterations = 0

                if iteration % 10 == 0:
                    logger.info(
                        f"Iteration {iteration}: Found {len(self.challenging_combinations)} challenging combinations"
                    )
                    self.save_progress(path, iteration)
            except Exception as e:
                logger.exception(f"Error during iteration {iteration}: {e}")
                continue

        self.save_progress(path, "final")
        # Sort and return challenging combinations
        sorted_combinations = dict(
            sorted(
                self.challenging_combinations.items(),
                key=lambda x: (x[1]["score"], x[1]["count"]),
                reverse=True,
            )
        )

        logger.info("MCTS completed. Found challenging concept combinations:")
        for concepts, stats in sorted_combinations.items():
            logger.info(
                f"Concepts: {concepts}, Score: {stats['score']:.2f}, Count: {stats['count']}"
            )

        return sorted_combinations

    def select_node(self) -> ChallengeNode:
        """
        Select node based on UCB but favoring challenging combinations.
        """
        current = random.choice([n for n in self.tree.nodes if n.parents])

        while current.children:
            if random.random() < 0.1:  # 10% random exploration
                current = random.choice(current.children)
            else:
                # Use UCB with challenge score
                current = max(
                    current.children,
                    key=lambda child: self.calculate_ucb(child),
                )

        return current

    def calculate_ucb(self, node: ChallengeNode) -> float:
        """
        Calculates the UCB value incorporating challenge metrics.
        Higher values are assigned to more challenging combinations.

        Args:
            node (ChallengeNode): The node for which to calculate the UCB value.

        Returns:
            float: The calculated UCB value.
        """
        if node.visits == 0:
            return float("inf")

        # Get average challenge score from node's run results
        challenge_scores = [
            self.calculate_challenge_score(result) for result in node.run_results
        ]
        avg_challenge = (
            sum(challenge_scores) / len(challenge_scores) if challenge_scores else 0
        )

        # UCB formula favoring challenging nodes
        exploitation = avg_challenge  # Higher challenge = higher exploitation
        total_visits = sum(parent.visits for parent in node.parents) or 1
        exploration = math.sqrt(math.log(total_visits) / node.visits)

        ucb_value = exploitation + self.exploration_weight * exploration
        return ucb_value

    def calculate_challenge_score(self, results: Dict) -> float:
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
        total_tests = (
            results.get("cumulative_tests_passed", 0)
            + results.get("cumulative_tests_failed", 0)
            + results.get("cumulative_tests_errored", 0)
        )

        # Invert success rate - higher means more challenging
        if total_tests > 0:
            success_rate = results.get("cumulative_tests_passed", 0) / total_tests
        else:
            success_rate = 0
        challenge_from_success = 1 - success_rate

        # More attempts means more challenging
        attempts = results.get("attempts_till_success", 1)
        attempt_factor = min(attempts / 3, 1.0)

        # Needing fixes means more challenging
        fixer_factor = 1.0 if results.get("fixed_by_problem_fixer") else 0.0

        # Weighted combination
        challenge_score = (
            challenge_from_success * 0.5  # Weight success rate highest
            + attempt_factor * 0.3  # Weight attempts next
            + fixer_factor * 0.2  # Weight fixes least
        )

        return challenge_score

    def simulate(self, node: ChallengeNode) -> float:
        """
        Simulates the execution of a node by running a coding challenge and calculates the score.

        Args:
            node (ChallengeNode): The node to simulate.

        Returns:
            float: The normalized score obtained from the simulation.
        """
        logger.debug(
            f"Simulating node: Difficulty={node.difficulty}, Concepts={node.concepts}"
        )
        challenge_results = self.environment.run_challenge(
            concept=node.concepts,
            difficulty_level=node.difficulty,
            max_attempts=MAX_ATTEMPTS,
        )
        self.update_node_data(node, challenge_results)
        score = self.calculate_challenge_score(challenge_results)
        node.run_results.append(challenge_results)
        logger.debug(f"Simulation completed with score: {score:.2f}")
        return score

    def expand_node(self, node: ChallengeNode) -> Optional[ChallengeNode]:
        """
        Expands a node by creating a new child node focused on exploring challenging concept combinations.
        The expansion can be by increasing difficulty or adding new concepts.

        Args:
            node (ChallengeNode): The node to expand.

        Returns:
            Optional[ChallengeNode]: The newly created child node or None if expansion isn't possible.
        """
        if node.depth >= self.max_depth:
            return None

        # Determine if the combination is challenging
        challenge_score = self.calculate_challenge_score(node.run_results[-1])

        if challenge_score > self.challenge_threshold:
            # Record as a challenging combination
            concept_key = tuple(sorted(node.concepts))
            if concept_key not in self.challenging_combinations:
                self.challenging_combinations[concept_key] = {
                    "score": challenge_score,
                    "count": 1,
                }
            else:
                existing = self.challenging_combinations[concept_key]
                existing["score"] = (
                    existing["score"] * existing["count"] + challenge_score
                ) / (existing["count"] + 1)
                existing["count"] += 1

            # Increase difficulty
            next_difficulty_idx = min(
                self.tree.difficulties.index(node.difficulty) + 1,
                len(self.tree.difficulties) - 1,
            )
            new_difficulty = self.tree.difficulties[next_difficulty_idx]

            # Keep same concepts
            new_concepts = list(node.concepts)
        else:
            # Try adding a new concept or increasing difficulty
            if random.random() < 0.5:
                next_difficulty_idx = min(
                    self.tree.difficulties.index(node.difficulty) + 1,
                    len(self.tree.difficulties) - 1,
                )
            else:
                next_difficulty_idx = max(
                    self.tree.difficulties.index(node.difficulty), 0
                )
            new_difficulty = self.tree.difficulties[next_difficulty_idx]

            new_concepts = list(node.concepts)
            if len(new_concepts) < 4:
                available_concepts = set(self.tree.concepts) - set(new_concepts)
                if available_concepts:
                    new_concepts.append(random.choice(list(available_concepts)))

        return self.tree.add_node(
            parent_nodes=[node],
            concepts=new_concepts,
            difficulty=new_difficulty,
            phase=2,
        )


class CompMCTS(ConceptMCTS):
    """
    Monte Carlo Tree Search implementation focusing on generating comprehensive coding challenges. Phase 3.
    Inherits common functionality from ConceptMCTS.
    """

    def __init__(
        self,
        environment: EnhancedCodingChallengeEnvironment,
        tree: Tree,
        variations_per_concept: int = 5,  # Generate multiple problems per concept combo
    ):
        super().__init__(environment, tree)
        self.challenging_nodes = []
        self.variations_per_concept = variations_per_concept
        self.node_selection_threshold = NODE_SELECTION_THRESHOLD

    def calculate_challenging_combinations(self) -> None:
        """
        Identifies challenging nodes from the tree based on a threshold.
        """
        for node in self.tree.nodes:
            if node.phase == 2 and node.value >= self.node_selection_threshold:
                self.challenging_nodes.append(node)

    def run(self):
        """Run comprehensive benchmark suite"""
        logger.info("Starting Concept Challenge MCTS")
        timestamp = datetime.now().strftime("%m%d_%H%M")
        experiment_name = f"{timestamp}_PHASE_THREE"
        path = os.path.join(os.getcwd(), "experiments", experiment_name)
        os.makedirs(path, exist_ok=True)

        self.calculate_challenging_combinations()
        logger.info(f"Found {len(self.challenging_nodes)} challenging nodes")
        for i, node in enumerate(self.challenging_nodes):
            try:
                run_results = self.environment.run_challenge(
                    concept=node.concepts,
                    difficulty_level=node.difficulty,
                    max_attempts=MAX_ATTEMPTS,
                    num_problems=self.variations_per_concept,
                )
                for attempt in run_results:
                    new_node = self.tree.add_node(
                        parent_nodes=[node],
                        concepts=node.concepts,
                        difficulty=node.difficulty,
                        phase=3,
                    )
                    new_node.challenge_description = attempt["problem_statement"]
                    for attempt_num, attempt_details in attempt["data_trail"].items():
                        node.problem_statement.setdefault(attempt_num, []).append(
                            attempt_details["problem_statement"]
                            if "problem_statement" in attempt_details
                            else []
                        )
                        node.solution_code.setdefault(attempt_num, []).append(
                            attempt_details["solution_code"]
                            if "solution_code" in attempt_details
                            else []
                        )
                        node.test_cases.setdefault(attempt_num, []).append(
                            attempt_details["test_cases"]
                            if "test_cases" in attempt_details
                            else []
                        )
                    new_node.run_results.append(attempt)
                    new_node.value = self.calculate_challenge_score(
                        new_node.run_results[-1]
                    )
            except Exception as e:
                logger.exception(f"Error during iteration {i}: {e}")
                pass

            self.tree.save_tree(file_name=path + f"/tree_{i}")
            self.tree.visualize_tree(file_name=path + f"/tree_{i}")

        self.tree.save_tree(file_name=path + "/tree_final")
        self.tree.visualize_tree(file_name=path + "/tree_final")
