import math
import os
from typing import Union

import yaml
from loguru import logger

with open(
    os.path.join(
        os.getcwd(),
        "configs.yml",
    ),
    "r",
) as f:
    configs = yaml.safe_load(f)

LEARNING_RATE = configs["learning_rate"]


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
        """

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

        logger.debug(
            f"Created node: Difficulty={difficulty}, Concepts={concepts}, Depth={depth}"
        )

    def update_node_score(self, reward: float) -> None:
        """
        Updates the node's value using a TD learning update.

        Parameters:
        - reward (float): The normalized reward between 0 and 1.

        Returns:
        - None
        """
        self.visits += 1
        self.value += LEARNING_RATE * (reward - self.value)

        logger.debug(
            f"Updated node value: New value={self.value:.2f}, Reward={reward:.2f}"
        )

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
            math.log(
                sum([parent.visits for parent in self.parents])
                if len(self.parents) > 1
                else 1
            )
            / self.visits
        )

        return exploitation + exploration_weight * exploration


if __name__ == "__main__":
    test_node = ChallengeNode("easy", ["loops"], "Write a loop to iterate over a list.")
