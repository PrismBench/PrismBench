import html
import pickle
from datetime import datetime
from itertools import combinations
from typing import Dict, Union

from graphviz import Digraph
from loguru import logger

from .node import ChallengeNode


class Tree:
    """
    A tree data structure for managing challenge nodes in the MCTS algorithm.

    This class handles the creation, management, and visualization of nodes
    representing different challenge combinations and difficulties.
    """

    def __init__(
        self,
        concepts: list,
        difficulties: list,
    ) -> None:
        """
        Initialize the Tree with concepts and difficulty levels.

        Args:
            concepts (list): List of concepts to initialize the tree with.
            difficulties (list): List of difficulty levels in ascending order.
        """
        self.concepts = concepts
        self.difficulties = difficulties
        self.nodes = []

        logger.info(f"Initialized tree with {len(concepts)} concepts and {len(difficulties)} difficulty levels")
        logger.debug(f"Concepts: {concepts}")
        logger.debug(f"Difficulties: {difficulties}")

    def initialize_tree(self) -> None:
        """
        Initializes the tree with the given concepts.

        Args:
            concepts (list): list of concepts to initialize the tree with.
        """
        logger.info("Initializing tree with root nodes and concept combinations")

        # first create the root nodes
        self.nodes = [
            ChallengeNode(
                difficulty="very easy",
                concepts=concept,
                challenge_description="",
            )
            for concept in self.concepts
        ]

        logger.debug(f"Created {len(self.nodes)} root nodes")

        # then create the rest of initial nodes by using pairs of root nodes
        initial_node_count = len(self.nodes)
        for node in list(combinations(self.nodes, 2)):
            self.add_node(node)

        total_combinations = len(self.nodes) - initial_node_count
        logger.info(
            f"Tree initialization complete: {len(self.nodes)} total nodes ({initial_node_count} root + {total_combinations} combinations)"
        )

    def add_node(
        self,
        parent_nodes: Union[ChallengeNode, list[ChallengeNode]],
        **kwargs,
    ) -> ChallengeNode:
        """
        Adds a new node to the tree based on the given parent nodes.

        Args:
            - parent_nodes (Union[ChallengeNode, list[ChallengeNode]]): The parent nodes to add the new node to.
            - kwargs: Additional keyword arguments to pass to the new node.
                - concepts (list): The concepts of the new node.
                - difficulty (str): The difficulty of the new node.
                - phase (int): The phase of the new node. Only used for Phases 2 and 3.

        Returns:
            ChallengeNode: The newly created or existing node.
        """

        if isinstance(parent_nodes, ChallengeNode):
            parent_nodes = [parent_nodes]

        if isinstance(parent_nodes, tuple):
            parent_nodes = list(parent_nodes)

        if "concepts" in kwargs:
            new_node_concepts = kwargs["concepts"]
            new_node_difficulty = kwargs["difficulty"]
        else:
            # calculate the concepts of the new node
            new_node_concepts = set([concept for parent_node in parent_nodes for concept in parent_node.concepts])

            # calculate the difficulty of the new node
            new_node_difficulty = self.assign_difficulty(parent_nodes)

        new_node_concepts_list = sorted(list(new_node_concepts)[:4])
        logger.debug(f"Creating node with concepts: {new_node_concepts_list}, difficulty: {new_node_difficulty}")

        # check if a node with the same concepts and difficulty already exists
        if "phase" not in kwargs:
            if kwargs.get("phase") != 3:
                for existing_node in self.nodes:
                    if (
                        sorted(existing_node.concepts) == new_node_concepts_list
                        and existing_node.difficulty == new_node_difficulty
                    ):
                        logger.debug(
                            f"Reusing existing node {existing_node.id} ({existing_node.concepts}, {existing_node.difficulty})"
                        )
                        return existing_node

        new_node = ChallengeNode(
            difficulty=new_node_difficulty,
            concepts=list(new_node_concepts)[:4],
            challenge_description="",
            parents=parent_nodes,
            depth=max([parent.depth for parent in parent_nodes]) + 1,
            phase=kwargs["phase"] if "phase" in kwargs else 1,
        )

        logger.debug(
            f"Created new node {new_node.id} ({new_node.concepts}, {new_node.difficulty}) at depth {new_node.depth}"
        )

        for parent_node in parent_nodes:
            parent_node.children.append(new_node)

        self.nodes.append(new_node)

        return new_node

    def remove_node(self, node: ChallengeNode) -> None:
        """
        Removes a node from the tree, cleaning up parent and child references.
        """
        # detach from parents
        parents = node.parents or []
        if isinstance(parents, tuple):
            parents = list(parents)
        elif isinstance(parents, ChallengeNode):
            parents = [parents]

        for parent in parents:
            try:
                parent.children.remove(node)
            except ValueError:
                logger.warning(f"Node {node.id} not found in parent {parent.id} children")

        # detach from children
        for child in node.children:
            child_parents = child.parents or []
            if not isinstance(child_parents, list):
                child_parents = [child_parents]
            try:
                child_parents.remove(node)
                child.parents = child_parents
            except ValueError:
                logger.warning(f"Node {node.id} not found in child {child.id} parents")

        # remove from the master list
        try:
            self.nodes.remove(node)
        except ValueError:
            logger.warning(f"Node {node.id} not found in tree.nodes")

        logger.info(f"Node {node.id} removed from tree")

    def assign_difficulty(self, parent_nodes: list[ChallengeNode]) -> str:
        """
        Assigns the difficulty of the new node based on the parent nodes.

        Args:
            parent_nodes (list[ChallengeNode]): list of parent nodes to assign the difficulty from.

        Returns:
            str: the difficulty of the new node.
        """
        parents_max_difficulty = max([self.difficulties.index(parent.difficulty) for parent in parent_nodes])
        parents_min_score = min([parent.value for parent in parent_nodes])

        try:
            new_node_difficulty = self.difficulties[parents_max_difficulty + 1]
            logger.debug(
                f"Increasing difficulty from {self.difficulties[parents_max_difficulty]} to {new_node_difficulty} (min parent score: {parents_min_score:.3f})"
            )
        except IndexError:
            new_node_difficulty = self.difficulties[parents_max_difficulty]
            logger.debug(f"Keeping max difficulty {new_node_difficulty} (already at highest level)")

        return new_node_difficulty

    def calculate_performance_score(self, results: Dict) -> float:
        """
        Calculate performance score for a node's results

        Args:
            results (Dict): The results of the node's run.
        returns:
            float: The performance score for the node.
        """
        total_tests = results["tests_passed_num"] + results["tests_failed_num"] + results["tests_errored_num"]

        success_rate = results["tests_passed_num"] / total_tests if total_tests > 0 else 0
        attempt_penalty = 0.2 * (results["attempt_num"]) if results["attempt_num"] else 0.6
        fixer_penalty = 0.3 if results["fixed_by_problem_fixer"] else 0

        performance_score = success_rate * 0.6 + (1 - attempt_penalty) * 0.25 + (1 - fixer_penalty) * 0.15

        logger.debug(
            f"Performance score calculation: success_rate={success_rate:.3f}, attempt_penalty={attempt_penalty:.3f}, fixer_penalty={fixer_penalty:.3f}, final_score={performance_score:.3f}"
        )

        return performance_score

    def visualize_tree(self, file_name: str = "tree") -> None:
        """
        Visualizes the tree using Graphviz with color coding for different phases.

        Args:
            file_name (str): The name of the file to save the tree visualization to. Defaults to "tree".
        """
        logger.info(f"Generating tree visualization with {len(self.nodes)} nodes")

        dot = Digraph(comment="MCTS Tree")
        dot.attr(rankdir="TB")
        dot.attr(
            "node",
            shape="box",
            style="rounded, filled",
            fontname="Helvetica",
            fontsize="12",
            penwidth="2",
        )
        # Define color schemes for different phases
        phase_colors = {
            1: {
                "fillcolor": "lightyellow",
                "color": "darkblue",
                "label_prefix": "Phase 1",
            },
            2: {
                "fillcolor": "lightgreen",
                "color": "darkgreen",
                "label_prefix": "Phase 2",
            },
            3: {
                "fillcolor": "lightblue",
                "color": "darkblue",
                "label_prefix": "Phase 3",
            },
        }

        # Add legend
        with dot.subgraph(name="cluster_legend") as legend:
            legend.attr(label="Legend")
            for phase, style in phase_colors.items():
                legend_node_name = f"legend_phase_{phase}"
                legend.node(
                    legend_node_name,
                    f"Phase {phase} Node",
                    style="filled",
                    fillcolor=style["fillcolor"],
                    color=style["color"],
                )

        # Add nodes with phase-specific styling
        edge_count = 0
        for node in self.nodes:
            phase = int(node.phase)  # Default to phase 1 if not marked
            style = phase_colors[phase]

            # Format the node metrics
            performance_metrics = ""

            # Construct the node label
            challenge_description = html.escape(node.challenge_description).replace("\n", "\\l")

            label = (
                f"{style['label_prefix']}\n"
                f"\nCONCEPTS:\l    {node.concepts}\l\n"
                f"DIFFICULTY:\l    {html.escape(node.difficulty)}\l\n"
                f"SCORE:\l    {html.escape(str(node.value))}\l\n"
                f"VISITS:\l    {html.escape(str(node.visits))}\l\n"
                f"{performance_metrics}\l\n"
                f"CHALLENGE DESCRIPTION:\l    {challenge_description}\l"
            )

            dot.node(
                str(id(node)),
                label,
                style="filled",
                fillcolor=style["fillcolor"],
                color=style["color"],
            )

            # Add edges to children
            for child in node.children:
                # Color edges based on performance improvement
                edge_color = "green"
                if node.value and child.value:
                    if child.value < node.value:
                        edge_color = "red"
                    elif child.value == node.value:
                        edge_color = "gray"

                dot.edge(str(id(node)), str(id(child)), color=edge_color, penwidth="2.0")
                edge_count += 1

        # Add graph title with timestamp
        dot.attr(label=f"MCTS Tree Visualization\nGenerated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Save in multiple formats
        formats_saved = []
        for fmt in ["svg", "pdf"]:
            try:
                dot.render(f"{file_name}", format=fmt, cleanup=True)
                formats_saved.append(fmt)
            except Exception as e:
                logger.warning(f"Failed to save visualization in {fmt} format: {e}")

        logger.info(f"Tree visualization saved as {file_name} in formats: {formats_saved}")
        logger.debug(f"Visualization stats: {len(self.nodes)} nodes, {edge_count} edges")

    def save_tree(self, file_name: str = "tree") -> None:
        """
        Saves the current tree structure to a file in pickle format.

        Args:
            file_name (str): The name of the file to save the tree to. Defaults to "tree".

        Returns:
            None
        """
        try:
            with open(f"{file_name}.pkl", "wb") as f:
                pickle.dump(self.nodes, f)
            logger.debug(f"Tree saved to {file_name}.pkl ({len(self.nodes)} nodes)")
        except Exception as e:
            logger.error(f"Failed to save tree to {file_name}.pkl: {e}")

    def load_tree(self, file_name: str = "tree") -> None:
        """
        Load the tree structure from a pickle file.

        Args:
            file_name (str): The base name of the file to load the tree from.
                             Defaults to "tree".

        Returns:
            None
        """
        try:
            with open(f"{file_name}.pkl", "rb") as f:
                self.nodes = pickle.load(f)
            logger.info(f"Tree loaded from {file_name}.pkl ({len(self.nodes)} nodes)")
        except FileNotFoundError:
            logger.error(f"Tree file {file_name}.pkl not found")
        except Exception as e:
            logger.error(f"Failed to load tree from {file_name}.pkl: {e}")

    def to_dict(self) -> dict:
        """
        Serializes the entire tree to a dictionary suitable for JSON export.

        Returns:
            dict: A dictionary with a list of all nodes and a mapping from id to node.
        """
        nodes_list = [node.to_dict() for node in self.nodes]

        tree_dict = {
            "nodes": nodes_list,
            "concepts": self.concepts,
            "difficulties": self.difficulties,
        }

        logger.debug(f"Tree serialized to dictionary: {len(nodes_list)} nodes")

        return tree_dict


if __name__ == "__main__":
    logger.info("Running tree.py as main module")

    tree = Tree(
        concepts=["concept1", "concept2", "concept3", "concept4"],
        difficulties=["very easy", "easy", "medium", "hard", "very hard"],
    )
    tree.initialize_tree()
    tree.save_tree(file_name="initial_tree_2")
    tree.visualize_tree(file_name="initial_tree_2")

    logger.info("Tree initialization and visualization complete")
