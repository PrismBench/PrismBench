import html
import pickle
from itertools import combinations
from typing import Dict, Union

from graphviz import Digraph
from tree import ChallengeNode


class Tree:
    def __init__(
        self,
        concepts: list,
        difficulties: list,
    ) -> None:
        self.concepts = concepts
        self.difficulties = difficulties

        self.nodes = []
        self._initialize_phase_markers()

    def _initialize_phase_markers(self):
        """Initialize phase_markers dictionary and mark existing nodes as phase 1"""
        if not hasattr(self, "phase_markers"):
            self.phase_markers = {}
            # Mark any existing nodes as phase 1
            for node in self.nodes:
                self.phase_markers[node] = 1

    def initialize_tree(self) -> None:
        """
        Initializes the tree with the given concepts.

        Args:
            concepts (list): list of concepts to initialize the tree with.
        """
        # first create the root nodes
        self.nodes = [
            ChallengeNode(
                difficulty="very easy",
                concepts=concept,
                challenge_description="",
            )
            for concept in self.concepts
        ]

        # then create the rest of initial nodes by using paris of root nodes
        for node in list(combinations(self.nodes, 2)):
            self.add_node(node)
        self._initialize_phase_markers()

    def add_node(
        self,
        parent_nodes: Union[ChallengeNode, list[ChallengeNode]],
        **kwargs,
    ) -> None:
        """
        Adds a new node to the tree based on the given parent nodes.

        Args:
            - parent_nodes (Union[ChallengeNode, list[ChallengeNode]]): The parent nodes to add the new node to.
            - kwargs: Additional keyword arguments to pass to the new node.
                - concepts (list): The concepts of the new node.
                - difficulty (str): The difficulty of the new node.
                - phase (int): The phase of the new node. Only used for Phases 2 and 3.
        """

        if "concepts" in kwargs:
            new_node_concepts = kwargs["concepts"]
            new_node_difficulty = kwargs["difficulty"]
        else:
            # calculate the concepts of the new node
            if isinstance(parent_nodes, ChallengeNode):
                new_node_concepts = parent_nodes.concepts
            else:
                new_node_concepts = set([concept for parent_node in parent_nodes for concept in parent_node.concepts])

            # calculate the difficulty of the new node
            new_node_difficulty = self.assign_difficulty(parent_nodes)

        new_node = ChallengeNode(
            difficulty=new_node_difficulty,
            concepts=list(new_node_concepts)[:4],
            challenge_description="",
            parents=parent_nodes,
            depth=parent_nodes[0].depth + 1,
            phase=kwargs["phase"] if "phase" in kwargs else 1,
        )

        for parent_node in parent_nodes:
            parent_node.children.append(new_node)

        self.nodes.append(new_node)

        self.phase_markers[new_node] = kwargs["phase"] if "phase" in kwargs else 1

        return new_node

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

        if parents_min_score > 0.3:
            try:
                new_node_difficulty = self.difficulties[parents_max_difficulty + 1]
            except IndexError:
                new_node_difficulty = self.difficulties[parents_max_difficulty]
        else:
            new_node_difficulty = (
                self.difficulties[parents_max_difficulty - 1] if parents_max_difficulty > 0 else "very easy"
            )

        return new_node_difficulty

    def calculate_performance_score(self, results: Dict) -> float:
        """
        Calculate performance score for a node's results

        Args:
            results (Dict): The results of the node's run.
        returns:
            float: The performance score for the node.
        """
        total_tests = (
            results["cumulative_tests_passed"]
            + results["cumulative_tests_failed"]
            + results["cumulative_tests_errored"]
        )

        success_rate = results["cumulative_tests_passed"] / total_tests if total_tests > 0 else 0
        attempt_penalty = 0.2 * (results["attempts_till_success"] - 1) if results["attempts_till_success"] else 0.6
        fixer_penalty = 0.3 if results["fixed_by_problem_fixer"] else 0

        return success_rate * 0.6 + (1 - attempt_penalty) * 0.25 + (1 - fixer_penalty) * 0.15

    def visualize_tree(self, file_name: str = "tree") -> None:
        """
        Visualizes the tree using Graphviz with color coding for different phases.

        Args:
            file_name (str): The name of the file to save the tree visualization to. Defaults to "tree".
        """
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
        for node in self.nodes:
            phase = int(node.phase)  # Default to phase 1 if not marked
            style = phase_colors[phase]

            # Format the node metrics
            performance_metrics = ""
            if node.run_results:
                avg_score = sum(self.calculate_performance_score(r) for r in node.run_results) / len(node.run_results)
                # performance_metrics = f"\nAvg Score: {avg_score:.2f}"

            # Format concepts with line breaks
            formatted_concepts = "\l    ".join(str(c) for c in node.concepts)

            label = (
                f"{style['label_prefix']}\n"
                f"\nCONCEPTS:\l    {formatted_concepts}\l\n"
                f"DIFFICULTY:\l    {html.escape(node.difficulty)}\l\n"
                f"SCORE:\l    {html.escape(str(f'{node.value:.2f}'))}\l\n"
                f"VISITS:\l    {html.escape(str(node.visits))}\l\n"
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

        # Add graph title with timestamp
        dot.attr(label=f"MCTS Tree Visualization-----{file_name}")

        # Save in multiple formats
        for fmt in ["svg", "pdf"]:
            dot.render(f"{file_name}", format=fmt, cleanup=True)

    def save_tree(self, file_name: str = "tree") -> None:
        """
        Saves the current tree structure to a file in pickle format.

        Args:
            file_name (str): The name of the file to save the tree to. Defaults to "tree".

        Returns:
            None
        """
        with open(f"{file_name}.pkl", "wb") as f:
            pickle.dump(self.nodes, f)
        with open(f"{file_name}_phases.pkl", "wb") as f:
            pickle.dump(self.phase_markers, f)

    def load_tree(self, file_name: str = "tree") -> None:
        """
        Load the tree structure from a pickle file.

        Args:
            file_name (str): The base name of the file to load the tree from.
                             Defaults to "tree".

        Returns:
            None
        """
        with open(f"{file_name}.pkl", "rb") as f:
            self.nodes = pickle.load(f)
        # with open(f"{file_name}_phases.pkl", "rb") as f:
        #     self.phase_markers = pickle.load(f)
        # self._initialize_phase_markers()


if __name__ == "__main__":
    tree = Tree(
        concepts=["concept1", "concept2", "concept3", "concept4"],
        difficulties=["very easy", "easy", "medium", "hard", "very hard"],
    )
    tree.initialize_tree()
    tree.load_tree(file_name="/Users/ahvra/Nexus/Prism/experiments/llama3.1-8b/final-1/1202_1200_PHASE_THREE/tree_27")
    tree.visualize_tree(file_name="llama3.1-8b")
