import sys
from pathlib import Path

from loguru import logger


class DataLoader:
    """Handles loading and finding MCTS tree data from experiment directories"""

    def __init__(self, experiment_path: str):
        """
        Initialize loader with path to experiment directory and phase

        Args:
            experiment_path: Path to experiment directory
        """
        self.experiment_path = Path(experiment_path)
        self.phase = self._find_latest_phase()
        self.tree_dir = self._find_phase_dir()
        self.tree_path = self._find_latest_tree()
        self.tree = self._load_tree()
        self._remove_empty_nodes()
        self.phase_nodes = [node for node in self.tree.nodes if int(node.phase) != 1]

    def _find_latest_phase(self) -> str:
        """Find the latest phase directory"""
        phase_dirs = [d.name for d in self.experiment_path.iterdir() if d.is_dir() and "phase" in d.name]
        return max(phase_dirs, key=lambda x: self._get_phase_number(x.split("_")[-1]))

    def _get_phase_number(self, phase: str) -> int:
        """Convert phase string to numeric value"""
        phase_map = {
            "one": 1,
            "two": 2,
            "three": 3,
        }
        return phase_map[phase]

    def _find_phase_dir(self) -> Path:
        """
        Find the directory containing results for the specified phase.

        This method iterates through the subdirectories of the experiment path
        to locate a directory whose name contains the specified phase. If such a directory
        is found, it is returned. If no such directory is found, a FileNotFoundError
        is raised.

        Returns:
            Path: The path to the directory containing phase results.

        Raises:
            FileNotFoundError: If no directory containing the phase name is found.
        """
        for subdir in self.experiment_path.iterdir():
            if subdir.is_dir() and self.phase in subdir.name:
                return subdir
        raise FileNotFoundError(f"No {self.phase} directory found in {self.experiment_path}")

    def _find_latest_tree(self) -> Path:
        """
        Find the latest tree file in the phase directory.

        This method first attempts to find a file named 'tree_final.pkl' in the
        specified directory. If this file exists, it is returned. If not, the method
        searches for files matching the pattern 'tree_*.pkl' and returns the one
        with the highest numeric suffix.

        Returns:
            Path: The path to the latest tree file.

        Raises:
            FileNotFoundError: If no tree files are found in the directory.
        """

        tree_files = [f for f in self.tree_dir.glob("*_tree_*.pkl")]
        if not tree_files:
            raise FileNotFoundError(f"No tree files found in {self.tree_dir}")
        # find the file that contains the word "final"
        final_tree = [f for f in tree_files if "final" in f.name]
        if final_tree:
            return Path(str(final_tree[0]).split(".pkl")[0])
        else:
            # Sort by the numeric part of the filename
            latest_tree = max(
                tree_files,
                key=lambda x: int(x.stem.split("_")[6]) if x.stem != "final" else -1,
            )
        return Path(str(latest_tree).split(".pkl")[0])

    def _load_tree(self):
        """Load the MCTS tree from pickle file"""
        try:
            from services.search.src.tree import Tree

            sys.modules["src.tree"] = sys.modules["services.search.src.tree"]
            sys.modules["src.tree.node"] = sys.modules["services.search.src.tree.node"]
            sys.modules["src.tree.tree"] = sys.modules["services.search.src.tree.tree"]
            _tree = Tree(
                concepts=[
                    "loops",
                    "conditionals",
                    "functions",
                    "data_structures",
                    "algorithms",
                    "error_handling",
                    "recursion",
                    "sorting",
                    "searching",
                    "dynamic_programming",
                ],
                difficulties=[
                    "very easy",
                    "easy",
                    "medium",
                    "hard",
                    "very hard",
                ],
            )
            _tree.load_tree(self.tree_path)
            return _tree
        except Exception as e:
            logger.error(f"Failed to load tree from {self.tree_path}: {e}")
            raise

    def _remove_empty_nodes(self):
        """Remove nodes that have no children and no challenge description"""
        for node in self.tree.nodes:
            if not node.children and not node.challenge_description:
                self.tree.remove_node(node)
                logger.info(f"Removed node: {node.difficulty} {node.concepts} {node.phase}")

    def get_phase_nodes(self):
        """Return the phase one nodes from the loaded tree"""
        return self.phase_nodes
