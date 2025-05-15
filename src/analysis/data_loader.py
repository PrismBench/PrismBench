import pickle
from pathlib import Path

from loguru import logger


class DataLoader:
    """Handles loading and finding MCTS tree data from experiment directories"""

    def __init__(self, experiment_path: str, phase: str = "PHASE_ONE"):
        """
        Initialize loader with path to experiment directory and phase

        Args:
            experiment_path: Path to experiment directory
            phase: Which phase to load data from ("PHASE_ONE", "PHASE_TWO", or "PHASE_THREE")
        """
        self.experiment_path = Path(experiment_path)
        self.phase = phase if phase != "PHASE_ONE_AND_TWO" else "PHASE_THREE"
        self.tree_dir = self._find_phase_dir()
        self.tree_path = self._find_latest_tree()
        self.tree = self._load_tree()
        if phase != "PHASE_ONE_AND_TWO":
            self.phase_nodes = [
                node for node in self.tree if node.phase == self._get_phase_number()
            ]
        else:
            self.phase_nodes = [node for node in self.tree if node.phase != 3]

    def _get_phase_number(self) -> int:
        """Convert phase string to numeric value"""
        phase_map = {
            "PHASE_ONE": 1,
            "PHASE_TWO": 2,
            "PHASE_THREE": 3,
        }
        return phase_map[self.phase]

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
        raise FileNotFoundError(
            f"No {self.phase} directory found in {self.experiment_path}"
        )

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
        # First try to find tree_final.pkl
        final_tree = self.tree_dir / "tree_final.pkl"
        if final_tree.exists():
            return final_tree

        # If tree_final.pkl doesn't exist, find the tree with highest number
        tree_files = [f for f in self.tree_dir.glob("tree_*.pkl")]
        if not tree_files:
            raise FileNotFoundError(f"No tree files found in {self.tree_dir}")

        # Sort by the numeric part of the filename
        latest_tree = max(
            tree_files,
            key=lambda x: int(x.stem.split("_")[1]) if x.stem != "tree_final" else -1,
        )
        return latest_tree

    def _load_tree(self):
        """Load the MCTS tree from pickle file"""
        try:
            with open(self.tree_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load tree from {self.tree_path}: {e}")
            raise

    def get_phase_nodes(self):
        """Return the phase one nodes from the loaded tree"""
        return self.phase_nodes
