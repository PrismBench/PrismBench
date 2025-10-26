from collections import defaultdict
from typing import Dict, List, Tuple


class ConceptMetricsAnalyzer:
    """Analyzes concept mastery metrics from phase one nodes"""

    def __init__(self, nodes: List):
        """Initialize analyzer with phase one nodes"""
        self.nodes = nodes

    def analyze(self) -> Dict:
        """
        Analyzes the mastery of concepts based on various metrics.

        Returns:
            Dict: A dictionary containing the following keys:
                - "concept_mastery_distribution": A processed distribution of concept mastery over time.
                - "concept_challenge_ranking": A ranking of concepts based on challenge metrics.
                - "performance_degradation": An analysis of performance impact due to complexity.
                - "difficulty_scaling_patterns": An analysis of difficulty progression patterns.
                - "concept_combinations": A dictionary of metrics for different concept combinations.
        """
        metrics = {
            "concept_success_over_time": defaultdict(lambda: defaultdict(list)),
            "concept_visit_stats": defaultdict(
                lambda: {
                    "available": 0,
                    "visited": 0,
                    "success_rate": 0,
                    "avg_value": 0,
                }
            ),
            "complexity_performance": defaultdict(lambda: defaultdict(list)),
            "difficulty_scaling": defaultdict(lambda: defaultdict(dict)),
            "concept_combinations": defaultdict(
                lambda: {
                    "success_rate": 0,
                    "total_attempts": 0,
                    "successful_attempts": 0,
                    "average_value": 0,
                    "difficulty_distribution": defaultdict(int),
                    "visits": 0,
                    "visits_by_difficulty": defaultdict(int),
                }
            ),
        }

        # Track availability and visits
        for node in self.nodes:
            for concept in node.concepts:
                metrics["concept_visit_stats"][concept]["available"] += 1
                if node.run_results:
                    metrics["concept_visit_stats"][concept]["visited"] += 1
                    metrics["concept_visit_stats"][concept]["avg_value"] += node.value

                    # Track success over time by difficulty level
                    success_rate = sum(
                        1 for r in node.run_results if r["success"]
                    ) / len(node.run_results)
                    metrics["concept_success_over_time"][concept][
                        node.difficulty
                    ].append((success_rate, node.visits))

                    # Track performance with increased complexity (number of concepts)
                    complexity = len(node.concepts)
                    metrics["complexity_performance"][concept][complexity].append(
                        (success_rate, node.value)
                    )

                    # Track difficulty scaling with visit ratio consideration
                    metrics["difficulty_scaling"][concept][node.difficulty] = {
                        "success_rate": success_rate,
                        "value": node.value,
                        "visits": node.visits,
                        "available": metrics["concept_visit_stats"][concept][
                            "available"
                        ],
                    }

        # Track concept combinations
        for node in self.nodes:
            if not node.run_results:
                continue

            # Sort concepts to ensure consistent combination keys
            concept_combo = tuple(sorted(node.concepts))

            # Update combination metrics
            success_count = sum(1 for r in node.run_results if r["success"])
            total_attempts = len(node.run_results)

            metrics["concept_combinations"][concept_combo][
                "total_attempts"
            ] += total_attempts
            metrics["concept_combinations"][concept_combo][
                "successful_attempts"
            ] += success_count
            metrics["concept_combinations"][concept_combo][
                "average_value"
            ] += node.value
            metrics["concept_combinations"][concept_combo]["difficulty_distribution"][
                node.difficulty
            ] += 1
            metrics["concept_combinations"][concept_combo]["visits"] += node.visits
            metrics["concept_combinations"][concept_combo]["visits_by_difficulty"][
                node.difficulty
            ] += node.visits

        # Calculate final success rates and averages for combinations
        for combo, data in metrics["concept_combinations"].items():
            if data["total_attempts"] > 0:
                data["success_rate"] = (
                    data["successful_attempts"] / data["total_attempts"]
                )
                data["average_value"] /= data["total_attempts"]

        return {
            "concept_mastery_distribution": self._process_temporal_mastery(
                metrics["concept_success_over_time"]
            ),
            "concept_challenge_ranking": self._rank_concepts_by_challenge(
                metrics["concept_visit_stats"], metrics["complexity_performance"]
            ),
            "performance_degradation": self._analyze_complexity_impact(
                metrics["complexity_performance"]
            ),
            "difficulty_scaling_patterns": self._analyze_difficulty_progression(
                metrics["difficulty_scaling"]
            ),
            "concept_combinations": dict(metrics["concept_combinations"]),
        }

    def _process_temporal_mastery(self, temporal_data: Dict) -> Dict:
        """Process temporal mastery data to show progression across difficulty levels"""
        mastery_distribution = {}

        for concept, difficulty_data in temporal_data.items():
            # Initialize difficulty progression
            progression = []

            # Sort by difficulty to track progression
            difficulty_order = ["very easy", "easy", "medium", "hard", "very hard"]
            sorted_difficulties = sorted(
                difficulty_data.keys(), key=lambda x: difficulty_order.index(x)
            )

            for difficulty in sorted_difficulties:
                success_visits = difficulty_data[difficulty]

                # Weight success rates by visit count
                weighted_success = sum(rate * visits for rate, visits in success_visits)
                total_visits = sum(visits for _, visits in success_visits)

                if total_visits > 0:
                    avg_success = weighted_success / total_visits
                    progression.append(
                        {
                            "difficulty": difficulty,
                            "success_rate": avg_success,
                            "visits": total_visits,
                        }
                    )

            mastery_distribution[concept] = progression

        return mastery_distribution

    def _rank_concepts_by_challenge(
        self,
        visit_stats: Dict,
        complexity_data: Dict,
    ) -> List[Tuple[str, float]]:
        """Rank concepts by their challenge level"""
        concept_scores = {}

        for concept, stats in visit_stats.items():
            if stats["available"] == 0:
                continue

            # Calculate visit ratio (how often MCTS chose to explore)
            visit_ratio = stats["visited"] / stats["available"]

            # Calculate average success at different complexities
            complexity_success = []
            for complexity, attempts in complexity_data[concept].items():
                if attempts:  # List of (success_rate, value) tuples
                    avg_success = sum(sr for sr, _ in attempts) / len(attempts)
                    avg_value = sum(val for _, val in attempts) / len(attempts)
                    complexity_success.append((avg_success, avg_value))

            if complexity_success:
                # Weight more complex scenarios higher
                weighted_success = sum(
                    success * value * (i + 1)
                    for i, (success, value) in enumerate(complexity_success)
                ) / sum(i + 1 for i in range(len(complexity_success)))

                # Combine visit ratio and success metrics
                # Lower score = more challenging
                challenge_score = (visit_ratio * 0.4) + (weighted_success * 0.6)
                concept_scores[concept] = challenge_score

        # Sort concepts by challenge score (ascending = more challenging first)
        return sorted(concept_scores.items(), key=lambda x: x[1])

    def _analyze_complexity_impact(self, complexity_data: Dict) -> Dict:
        """Analyze how performance degrades with increasing concept complexity"""
        degradation_patterns = {}

        for concept, complexity_attempts in complexity_data.items():
            complexity_levels = sorted(complexity_attempts.keys())
            degradation_curve = []

            baseline = None
            for complexity in complexity_levels:
                attempts = complexity_attempts[complexity]
                if not attempts:
                    continue

                # Calculate average success and value at this complexity
                avg_success = sum(sr for sr, _ in attempts) / len(attempts)
                avg_value = sum(val for _, val in attempts) / len(attempts)

                if baseline is None:
                    baseline = avg_success

                # Calculate relative performance compared to baseline
                relative_performance = avg_success / baseline if baseline > 0 else 0

                degradation_curve.append(
                    {
                        "complexity": complexity,
                        "relative_performance": relative_performance,
                        "absolute_success": avg_success,
                        "value_convergence": avg_value,
                        "sample_size": len(attempts),
                    }
                )

            degradation_patterns[concept] = degradation_curve

        return degradation_patterns

    def _analyze_difficulty_progression(self, difficulty_data: Dict) -> Dict:
        """Analyze how performance scales across difficulty levels"""
        scaling_patterns = {}

        for concept, difficulty_stats in difficulty_data.items():
            difficulty_levels = sorted(difficulty_stats.keys())
            scaling_curve = []

            for difficulty in difficulty_levels:
                stats = difficulty_stats[difficulty]

                # Calculate visit ratio for this difficulty
                visit_ratio = (
                    stats["visits"] / stats["available"]
                    if stats["available"] > 0
                    else 0
                )

                # Combine success rate with visit patterns
                adjusted_success = stats["success_rate"] * (0.7 + 0.3 * visit_ratio)

                scaling_curve.append(
                    {
                        "difficulty": difficulty,
                        "success_rate": stats["success_rate"],
                        "visit_ratio": visit_ratio,
                        "adjusted_success": adjusted_success,
                        "value_convergence": stats["value"],
                    }
                )

            scaling_patterns[concept] = scaling_curve

        return scaling_patterns
