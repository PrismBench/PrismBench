from collections import defaultdict
from typing import Dict, List

import numpy as np


class TreeMetricsAnalyzer:
    """Analyzes tree growth and structure metrics from phase one nodes"""

    def __init__(self, nodes: List):
        """Initialize analyzer with phase one nodes"""
        self.nodes = nodes

    def analyze(self) -> Dict:
        """Analyze tree growth and structure metrics"""
        metrics = {
            "nodes_by_depth": defaultdict(int),
            "nodes_by_depth_and_concept": defaultdict(lambda: defaultdict(int)),
            "nodes_by_depth_and_difficulty": defaultdict(lambda: defaultdict(int)),
            "breadth_by_depth": defaultdict(int),
            "convergence_iterations": defaultdict(list),
            "convergence_by_difficulty": defaultdict(lambda: defaultdict(list)),
            "path_success": defaultdict(list),
            "path_success_by_concept": defaultdict(lambda: defaultdict(list)),
            "balance_metrics": defaultdict(float),
            "branching_factors": defaultdict(list),
            "concept_depth_distribution": defaultdict(lambda: defaultdict(int)),
            "successful_path_lengths": [],
            "failed_path_lengths": [],
        }

        # Analyze tree structure
        for node in self.nodes:
            depth = node.depth
            metrics["nodes_by_depth"][depth] += 1

            # Track by concept and difficulty
            for concept in node.concepts:
                metrics["nodes_by_depth_and_concept"][depth][concept] += 1
                metrics["concept_depth_distribution"][concept][depth] += 1
            metrics["nodes_by_depth_and_difficulty"][depth][node.difficulty] += 1

            # Track branching factors
            if node.children:
                metrics["branching_factors"][depth].append(len(node.children))

            # Track path success rates with more detail
            if node.parents:
                path = self._get_path_to_root(node)
                path_success = np.mean(
                    [
                        (
                            1
                            if n.run_results
                            and any(r["success"] for r in n.run_results)
                            else 0
                        )
                        for n in path
                    ]
                )
                path_length = len(path)

                if path_success > 0.5:
                    metrics["successful_path_lengths"].append(path_length)
                else:
                    metrics["failed_path_lengths"].append(path_length)

                metrics["path_success"][path_length].append(path_success)
                for concept in node.concepts:
                    metrics["path_success_by_concept"][concept][path_length].append(
                        path_success
                    )

            # Track convergence with more detail
            if node.run_results:
                iterations = len(node.run_results)
                metrics["convergence_iterations"][node.concepts[0]].append(iterations)
                metrics["convergence_by_difficulty"][node.difficulty][
                    node.concepts[0]
                ].append(iterations)

        # Calculate advanced tree balance metrics
        total_nodes = len(self.nodes)
        max_depth = max(metrics["nodes_by_depth"].keys())
        avg_branching = np.mean(
            [np.mean(factors) for factors in metrics["branching_factors"].values()]
        )

        metrics["balance_metrics"].update(
            {
                "depth_ratio": max_depth / np.log2(total_nodes + 1),
                "breadth_variance": np.var(list(metrics["breadth_by_depth"].values())),
                "avg_branching_factor": avg_branching,
                "depth_utilization": len(metrics["nodes_by_depth"]) / max_depth,
                "path_length_ratio": (
                    np.mean(metrics["successful_path_lengths"])
                    / np.mean(metrics["failed_path_lengths"])
                    if metrics["failed_path_lengths"]
                    else 1
                ),
            }
        )

        return {
            "tree_growth_patterns": dict(metrics["nodes_by_depth"]),
            "nodes_by_concept": dict(metrics["nodes_by_depth_and_concept"]),
            "nodes_by_difficulty": dict(metrics["nodes_by_depth_and_difficulty"]),
            "depth_breadth_stats": {
                "max_depth": max_depth,
                "branching_factors": dict(metrics["branching_factors"]),
            },
            "convergence_speeds": {
                concept: np.mean(iters)
                for concept, iters in metrics["convergence_iterations"].items()
            },
            "convergence_by_difficulty": {
                diff: {
                    concept: np.mean(iters) for concept, iters in concept_data.items()
                }
                for diff, concept_data in metrics["convergence_by_difficulty"].items()
            },
            "path_success_rates": {
                depth: np.mean(rates)
                for depth, rates in metrics["path_success"].items()
            },
            "path_success_by_concept": {
                concept: {depth: np.mean(rates) for depth, rates in depth_data.items()}
                for concept, depth_data in metrics["path_success_by_concept"].items()
            },
            "tree_balance_metrics": dict(metrics["balance_metrics"]),
            "concept_depth_distribution": dict(metrics["concept_depth_distribution"]),
        }

    def _get_path_to_root(self, node) -> List:
        """Get path from node to root"""
        path = [node]
        current = node
        while current.parents:
            current = current.parents[0]  # Take first parent for simplicity
            path.append(current)
        return path
