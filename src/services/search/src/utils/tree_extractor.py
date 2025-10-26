import glob
import json
import os
import pickle
import re
from collections import defaultdict
from typing import List, Optional, Set, Tuple


class TreeExtractor:
    def __init__(self, experiments_dir: str = "experiments"):
        self.experiments_dir = experiments_dir
        self.problems_by_concept = defaultdict(lambda: defaultdict(list))
        self.problems_by_difficulty = defaultdict(list)
        self.problems_by_combination = defaultdict(list)
        self.seen_titles = set()  # Track titles we've seen

    def find_tree_files(self) -> List[str]:
        """Find all relevant tree files in PHASE_TWO directories recursively."""
        tree_files = []

        # Walk through all subdirectories
        for root, dirs, files in os.walk(self.experiments_dir):
            # Check if this directory contains "PHASE_TWO"
            if "PHASE_TWO" in root:
                # Try to find tree_final.pkl first
                final_tree = os.path.join(root, "tree_final.pkl")
                if os.path.exists(final_tree):
                    tree_files.append(final_tree)
                    continue

                # If no final tree, find the highest numbered tree file
                numbered_trees = glob.glob(os.path.join(root, "tree_*.pkl"))
                if numbered_trees:
                    # Extract numbers from filenames and find highest
                    numbers = [int(re.findall(r"\d+", f)[-1]) for f in numbered_trees if re.findall(r"\d+", f)]
                    if numbers:
                        max_num = max(numbers)
                        tree_files.append(os.path.join(root, f"tree_{max_num}.pkl"))

        return tree_files

    def load_tree(self, tree_file: str) -> Optional[object]:
        """Load a pickle tree file."""
        try:
            with open(tree_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading tree file {tree_file}: {e}")
            return None

    def extract_node_info(self, node) -> Tuple[str, Set[str], str]:
        """Extract relevant information from a node."""
        difficulty = getattr(node, "difficulty", "unknown")
        concepts = set(getattr(node, "concepts", []))
        challenge_desc = getattr(node, "challenge_description", "")
        return difficulty, concepts, challenge_desc

    def extract_challenge_title(self, description: str) -> str:
        """Extract the title from the challenge description."""
        if not description:
            return "Untitled Challenge"

        # Look for the title pattern "## Title\n"
        match = re.match(r"^##\s+([^\n]+)", description)
        if match:
            return match.group(1).strip()
        return "Untitled Challenge"

    def process_tree(self, tree) -> None:
        """Process all nodes in a tree and organize their information."""
        for node in tree:
            difficulty, concepts, challenge_desc = self.extract_node_info(node)

            if not challenge_desc or not concepts:
                continue

            # Ensure consistent ordering of concepts
            sorted_concepts = sorted(concepts)

            # Extract challenge title
            challenge_title = self.extract_challenge_title(challenge_desc)

            # Skip if we've seen this title before
            if challenge_title in self.seen_titles:
                continue

            self.seen_titles.add(challenge_title)

            # Create challenge data and store it
            challenge_data = {
                "title": challenge_title,
                "description": challenge_desc,
                "concepts": sorted_concepts,
                "difficulty": difficulty,
            }

            # Store by exact concept combination with sorted key
            combo_key = ",".join(sorted_concepts)

            # Store by concept combination
            self.problems_by_combination[combo_key].append(challenge_data)

            # Store by difficulty with full concept context
            self.problems_by_difficulty[difficulty].append(challenge_data)

            # For concept indexing, store reference to the full combination
            for concept in sorted_concepts:
                self.problems_by_concept[concept][difficulty].append(
                    {"combination": combo_key, "challenge": challenge_data}
                )

    def extract_all(self) -> None:
        """Process all tree files and extract their information."""
        tree_files = self.find_tree_files()
        for tree_file in tree_files:
            print(f"Processing {tree_file}")
            tree = self.load_tree(tree_file)
            if tree:
                self.process_tree(tree)

    def save_to_json(self, output_dir: str = "extracted_problems") -> None:
        """Save the organized problems to JSON files."""
        os.makedirs(output_dir, exist_ok=True)

        # Save problems by concept
        with open(os.path.join(output_dir, "problems_by_concept.json"), "w") as f:
            json.dump(self.problems_by_concept, f, indent=2)

        # Save problems by difficulty
        with open(os.path.join(output_dir, "problems_by_difficulty.json"), "w") as f:
            json.dump(self.problems_by_difficulty, f, indent=2)

        # Save problems by concept combination
        with open(os.path.join(output_dir, "problems_by_combination.json"), "w") as f:
            json.dump(self.problems_by_combination, f, indent=2)


def main():
    extractor = TreeExtractor()
    extractor.extract_all()
    extractor.save_to_json()


if __name__ == "__main__":
    main()
