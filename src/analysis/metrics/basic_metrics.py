from collections import defaultdict
from typing import Dict, List

import numpy as np


class BasicMetricsAnalyzer:
    """Analyzes basic performance metrics from phase one nodes"""

    def __init__(self, nodes: List):
        """Initialize analyzer with phase one nodes"""
        self.nodes = nodes

    def analyze(self) -> Dict:
        """
        Calculate basic performance metrics for phase one nodes.

        Returns:
            Dict: A dictionary containing the following keys:
            - "success_rates_by_concept": A dictionary mapping each concept to its
              average success rate.
            - "success_rates_by_difficulty": A dictionary mapping each difficulty
              level to its average success rate.
            - "avg_attempts_by_concept": A dictionary mapping each concept to its
              average number of attempts till success.
            - "avg_attempts_by_difficulty": A dictionary mapping each difficulty
              level to its average number of attempts till success.
            - "fixer_intervention_rate_difficulty": A dictionary mapping each
              difficulty level to its fixer intervention count.
            - "fixer_intervention_rate_concept": A dictionary mapping each concept
              to its fixer intervention count.
        """
        metrics = {
            "success_rates_by_concept": defaultdict(list),
            "success_rates_by_difficulty": defaultdict(list),
            "avg_attempts_concepts": defaultdict(list),
            "avg_attempts_difficulty": defaultdict(list),
            "fixer_interventions_by_difficulty": defaultdict(int),
            "fixer_interventions_by_concept": defaultdict(int),
            "attempt_distributions": defaultdict(list),
        }

        for node in self.nodes:
            if not node.run_results:
                continue

            # Process each run result
            for result in node.run_results:
                # Success rates by concept
                for concept in node.concepts:
                    metrics["success_rates_by_concept"][concept].append(
                        1 if result["success"] else 0
                    )

                # Success rates by difficulty
                metrics["success_rates_by_difficulty"][node.difficulty].append(
                    1 if result["success"] else 0
                )

                # Average attempts
                for concept in node.concepts:
                    metrics["avg_attempts_concepts"][concept].append(
                        result["attempts_till_success"] or 3
                    )

                metrics["avg_attempts_difficulty"][node.difficulty].append(
                    result["attempts_till_success"] or 3
                )

                # Problem fixer interventions
                if result["attempts_till_success"] == 3:
                    if result.get("fixed_by_problem_fixer"):
                        metrics["fixer_interventions_by_difficulty"][
                            node.difficulty
                        ] += 1

                        for concept in node.concepts:
                            metrics["fixer_interventions_by_concept"][concept] += 1

        # Calculate averages and format results
        return {
            "success_rates_by_concept": {
                concept: np.mean(rates)
                for concept, rates in metrics["success_rates_by_concept"].items()
            },
            "success_rates_by_difficulty": {
                diff: np.mean(rates)
                for diff, rates in metrics["success_rates_by_difficulty"].items()
            },
            "avg_attempts_by_concept": {
                concept: np.mean(attempts)
                for concept, attempts in metrics["avg_attempts_concepts"].items()
            },
            "avg_attempts_by_difficulty": {
                diff: np.mean(attempts)
                for diff, attempts in metrics["avg_attempts_difficulty"].items()
            },
            "fixer_intervention_rate_difficulty": metrics[
                "fixer_interventions_by_difficulty"
            ],
            "fixer_intervention_rate_concept": metrics[
                "fixer_interventions_by_concept"
            ],
        }
