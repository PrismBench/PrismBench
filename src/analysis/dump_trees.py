import json
import sys

from services.search.src.tree import Tree

if __name__ == "__main__":
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

    _tree.load_tree(file_name="/PrismBench/experiments/gpt-oss-20b/final-3/phase_three/phase_3_tree_phase_3_final")
    for node in _tree.nodes:
        if not node.children:
            if not node.challenge_description:
                print("removing node", node.difficulty, node.concepts, node.phase)
                _tree.remove_node(node)

    x = _tree.to_dict()
    with open("tree.json", "w") as f:
        json.dump(x, f)
