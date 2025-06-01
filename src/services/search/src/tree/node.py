import math
from typing import Union
from uuid import uuid4

from loguru import logger


class ChallengeNode:
    def __init__(
        self,
        difficulty: str,
        concepts: list[str],
        challenge_description: str,
        parents: Union["ChallengeNode", list["ChallengeNode"], None] = None,
        depth: int = 0,
        phase: int = 1,
    ):
        """
        Initializes a new node for the MCTS tree.

        Parameters:
        - difficulty (str): The difficulty level of the challenge.
        - concepts (list): The list of concepts related to the challenge.
        - challenge_description (str): The description of the challenge.
        - parents (Union[ChallengeNode, list[ChallengeNode], None], optional): The parent nodes of the current node.
            Defaults to None.
        - depth (int, optional): The depth of the current node in the tree. Defaults to 0.
        - phase (int, optional): The phase of the current node. Defaults to 1.
        """
        self.id = str(uuid4())

        self.difficulty = difficulty
        self.concepts = [concepts] if isinstance(concepts, str) else concepts
        self.challenge_description = challenge_description

        self.problem_statement = {}
        self.solution_code = {}
        self.test_cases = {}
        self.problem_fixer = {}

        self.parents = parents
        self.children = []
        self.depth = depth

        self.visits = 0
        self.successes = 0
        self.failures = 0
        self.score = 0
        self.phase = phase

        self.run_results = []
        self.value = 0.0  # Initialize the node's value

        logger.debug(f"Created node: Difficulty={difficulty}, Concepts={concepts}, Depth={depth}")

    def get_node_ancestors_ids(self) -> list[str]:
        """
        Returns a list of all ancestor node IDs.

        Returns:
        - list[str]: A list of all ancestor node IDs.
        """
        ancestor_ids = set()
        current_nodes = self.parents if self.parents else []

        while current_nodes:
            next_nodes = []
            for node in current_nodes:
                if node.id not in ancestor_ids:
                    ancestor_ids.add(node.id)
                    if node.parents:
                        next_nodes.extend(node.parents)
            current_nodes = next_nodes
        return list(ancestor_ids)

    def update_node_score(self, learning_rate: float, reward: float) -> None:
        """
        Updates the node's value using a TD learning update.

        Parameters:
        - reward (float): The normalized reward between 0 and 1.

        Returns:
        - None
        """
        self.visits += 1
        self.value += learning_rate * (reward - self.value)

        logger.debug(f"Updated node value: New value={self.value:.2f}, Reward={reward:.2f}")

    def ucb1(self, exploration_weight=1.414) -> float:
        """
        Calculates the UCB1 (Upper Confidence Bound 1) value for a node in a tree search.

        Parameters:
            exploration_weight (float): The exploration weight to balance exploration and exploitation.
                Default is 1.414.

        Returns:
            float: The UCB1 value for the node.
        """

        if self.visits == 0:
            return float("inf")

        exploitation = self.value
        exploration = math.sqrt(
            math.log(sum([parent.visits for parent in self.parents]) if len(self.parents) > 1 else 1) / self.visits
        )

        return exploitation + exploration_weight * exploration

    def to_dict(self) -> dict:
        """
        Serializes the ChallengeNode to a dictionary suitable for JSON export.
        Only includes basic fields and references children by their IDs to avoid recursion.

        Returns:
            dict: A dictionary representation of the node.
        """
        return {
            "id": self.id,
            "difficulty": self.difficulty,
            "concepts": self.concepts,
            "challenge_description": self.challenge_description,
            "problem_statement": self.problem_statement,
            "solution_code": self.solution_code,
            "test_cases": self.test_cases,
            "problem_fixer": self.problem_fixer,
            "depth": self.depth,
            "visits": self.visits,
            "successes": self.successes,
            "failures": self.failures,
            "score": self.score,
            "phase": self.phase,
            "run_results": self.run_results,
            "value": self.value,
            "children": [child.id for child in self.children],
            "parents": [parent.id for parent in self.parents] if self.parents else [],
        }


if __name__ == "__main__":
    test_node = ChallengeNode("easy", ["loops"], "Write a loop to iterate over a list.")
