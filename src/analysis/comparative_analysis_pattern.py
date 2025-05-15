"""
Comparative Analysis Module

This module implements comparative analysis of models' performance and pattern usage
across different concept combinations and difficulty levels.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class PatternAnalysis:
    """Analysis of a pattern's effectiveness."""

    usage_count: int
    success_rate: float
    concept_correlations: Dict[str, float]  # concept -> correlation score
    difficulty_distribution: Dict[str, int]  # difficulty -> count


@dataclass
class ConceptComboStats:
    """Statistics for a specific concept combination across models."""

    concepts: List[str]
    difficulty: str
    model_performances: Dict[str, Dict[str, Any]]  # model_name -> performance metrics

    def get_best_model(self) -> str:
        """Returns the name of the model with highest success rate."""
        return max(self.model_performances.items(), key=lambda x: x[1]["success_rate"])[
            0
        ]

    def get_most_patterns(self) -> str:
        """Returns the name of the model that used the most patterns."""
        return max(
            self.model_performances.items(), key=lambda x: len(x[1]["patterns"])
        )[0]


class ComparativeAnalyzer:
    """Analyzes and compares model performances across concept combinations."""

    def __init__(self, analysis_file: str):
        """
        Initialize the analyzer with the path to the analysis results.

        Args:
            analysis_file: Path to the phase 3 pattern analysis JSON file
        """
        self.analysis_file = Path(analysis_file)
        with open(self.analysis_file, "r") as f:
            self.data = json.load(f)

        self.models = list(self.data["models"].keys())
        self.concept_combinations = self._get_all_concept_combinations()

    def _get_all_concept_combinations(self) -> Dict[str, ConceptComboStats]:
        """
        Extract all unique concept combinations across all models and their stats.

        Returns:
            Dictionary mapping concept-difficulty string to ConceptComboStats
        """
        combinations = {}

        for model_name, model_data in self.data["models"].items():
            for combo in model_data["concept_combinations"]:
                # Create a key that uniquely identifies this concept-difficulty combination
                key = f"{'-'.join(sorted(combo['concepts']))}-{combo['difficulty']}"

                if key not in combinations:
                    combinations[key] = ConceptComboStats(
                        concepts=combo["concepts"],
                        difficulty=combo["difficulty"],
                        model_performances={},
                    )

                # Add this model's performance for this combination
                combinations[key].model_performances[model_name] = {
                    "success_rate": combo["success_rate"],
                    "avg_attempts": combo["avg_attempts"],
                    "patterns": combo["patterns"],
                }

        return combinations

    def analyze_model_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze each model's capabilities across different concept combinations.

        Returns:
            Dictionary containing capability metrics for each model
        """
        capabilities = {}

        for model_name in self.models:
            model_stats = {
                "total_combinations": 0,
                "difficulty_distribution": defaultdict(int),
                "concept_coverage": defaultdict(int),
                "success_by_difficulty": defaultdict(list),
                "most_successful_concepts": [],
                "challenging_concepts": [],
                "favorite_patterns": defaultdict(int),
            }

            # Analyze each combination this model attempted
            for combo in self.concept_combinations.values():
                if model_name not in combo.model_performances:
                    continue

                perf = combo.model_performances[model_name]
                model_stats["total_combinations"] += 1
                model_stats["difficulty_distribution"][combo.difficulty] += 1

                # Track success rate by difficulty
                model_stats["success_by_difficulty"][combo.difficulty].append(
                    perf["success_rate"]
                )

                # Count concept occurrences
                for concept in combo.concepts:
                    model_stats["concept_coverage"][concept] += 1

                # Track pattern usage
                for pattern in perf["patterns"]:
                    model_stats["favorite_patterns"][pattern] += 1

            # Calculate average success rate per difficulty
            for diff, rates in model_stats["success_by_difficulty"].items():
                model_stats["success_by_difficulty"][diff] = sum(rates) / len(rates)

            # Find most and least successful concepts
            concept_success = defaultdict(list)
            for combo in self.concept_combinations.values():
                if model_name not in combo.model_performances:
                    continue
                for concept in combo.concepts:
                    concept_success[concept].append(
                        combo.model_performances[model_name]["success_rate"]
                    )

            # Calculate average success rate per concept
            concept_avg_success = {
                concept: sum(rates) / len(rates)
                for concept, rates in concept_success.items()
            }

            # Sort concepts by success rate
            sorted_concepts = sorted(
                concept_avg_success.items(), key=lambda x: x[1], reverse=True
            )

            model_stats["most_successful_concepts"] = sorted_concepts[:3]
            model_stats["challenging_concepts"] = sorted_concepts[-3:]

            # Sort patterns by frequency
            model_stats["favorite_patterns"] = dict(
                sorted(
                    model_stats["favorite_patterns"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:10]
            )

            capabilities[model_name] = model_stats

        return capabilities

    def get_concept_difficulty_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Create a matrix of success rates for each concept-difficulty pair.

        Returns:
            Dictionary mapping models to their concept-difficulty success rates
        """
        matrix = {model: defaultdict(list) for model in self.models}

        for combo in self.concept_combinations.values():
            for model_name, perf in combo.model_performances.items():
                key = f"{'-'.join(sorted(combo.concepts))}-{combo.difficulty}"
                matrix[model_name][key] = perf["success_rate"]

        return {model: dict(rates) for model, rates in matrix.items()}

    def analyze_pattern_effectiveness(self) -> Dict[str, Dict[str, PatternAnalysis]]:
        """
        Analyze how effectively each model uses different patterns across concepts.

        Returns:
            Dictionary mapping model names to their pattern effectiveness analysis
        """
        pattern_analysis = {model: {} for model in self.models}

        for model_name in self.models:
            # Track pattern statistics
            pattern_stats = defaultdict(
                lambda: {
                    "usage_count": 0,
                    "success_rates": [],
                    "concept_usage": defaultdict(
                        list
                    ),  # concept -> list of success rates
                    "difficulty_count": defaultdict(int),
                }
            )

            # Analyze each combination for pattern usage
            for combo in self.concept_combinations.values():
                if model_name not in combo.model_performances:
                    continue

                perf = combo.model_performances[model_name]
                success_rate = perf["success_rate"]

                for pattern, frequency in perf["patterns"].items():
                    pattern_stats[pattern]["usage_count"] += 1
                    pattern_stats[pattern]["success_rates"].append(success_rate)
                    pattern_stats[pattern]["difficulty_count"][combo.difficulty] += 1

                    # Track success rate for each concept this pattern was used with
                    for concept in combo.concepts:
                        pattern_stats[pattern]["concept_usage"][concept].append(
                            success_rate
                        )

            # Calculate final statistics for each pattern
            for pattern, stats in pattern_stats.items():
                avg_success = sum(stats["success_rates"]) / len(stats["success_rates"])

                # Calculate correlation with concepts
                concept_correlations = {}
                for concept, rates in stats["concept_usage"].items():
                    if (
                        len(rates) > 1
                    ):  # Need at least 2 points for meaningful correlation
                        concept_avg = sum(rates) / len(rates)
                        correlation = (
                            concept_avg / avg_success if avg_success > 0 else 0
                        )
                        concept_correlations[concept] = correlation

                pattern_analysis[model_name][pattern] = PatternAnalysis(
                    usage_count=stats["usage_count"],
                    success_rate=avg_success,
                    concept_correlations=concept_correlations,
                    difficulty_distribution=stats["difficulty_count"],
                )

        return pattern_analysis

    def identify_pattern_strengths_weaknesses(
        self,
    ) -> Dict[str, Dict[str, List[Tuple[str, float]]]]:
        """
        Identify patterns that are particularly effective or ineffective for each model.

        Returns:
            Dictionary mapping models to their pattern strengths and weaknesses
        """
        pattern_effectiveness = self.analyze_pattern_effectiveness()
        insights = {}

        for model_name, patterns in pattern_effectiveness.items():
            # Filter patterns with significant usage (used more than once)
            significant_patterns = {
                pattern: analysis
                for pattern, analysis in patterns.items()
                if analysis.usage_count > 1
            }

            if not significant_patterns:
                continue

            # Calculate average success rate for this model
            avg_model_success = sum(
                p.success_rate for p in significant_patterns.values()
            ) / len(significant_patterns)

            # Identify strengths and weaknesses
            pattern_scores = [
                (pattern, analysis.success_rate / avg_model_success)
                for pattern, analysis in significant_patterns.items()
            ]
            sorted_patterns = sorted(pattern_scores, key=lambda x: x[1], reverse=True)

            insights[model_name] = {
                "strengths": sorted_patterns[:5],  # Top 5 most effective patterns
                "weaknesses": sorted_patterns[-5:],  # Bottom 5 least effective patterns
                "concept_specialties": [],  # Will be populated below
            }

            # Identify patterns that are particularly effective for specific concepts
            concept_patterns = defaultdict(list)
            for pattern, analysis in significant_patterns.items():
                for concept, correlation in analysis.concept_correlations.items():
                    if (
                        correlation > 1.2
                    ):  # Pattern is 20% more effective than average for this concept
                        concept_patterns[concept].append((pattern, correlation))

            # Sort and add top patterns for each concept
            for concept, patterns in concept_patterns.items():
                sorted_concept_patterns = sorted(
                    patterns, key=lambda x: x[1], reverse=True
                )
                if sorted_concept_patterns:
                    insights[model_name]["concept_specialties"].append(
                        {
                            "concept": concept,
                            "effective_patterns": sorted_concept_patterns[
                                :3
                            ],  # Top 3 patterns for this concept
                        }
                    )

        return insights

    def get_pattern_effectiveness(self) -> Dict[str, Dict[str, float]]:
        """
        Analyze how effective different patterns are for each model.

        Returns:
            Dictionary mapping models to their pattern effectiveness scores
        """
        effectiveness = {model: defaultdict(list) for model in self.models}

        for combo in self.concept_combinations.values():
            for model_name, perf in combo.model_performances.items():
                success_rate = perf["success_rate"]
                for pattern in perf["patterns"]:
                    effectiveness[model_name][pattern].append(success_rate)

        # Calculate average success rate for each pattern
        return {
            model: {
                pattern: sum(rates) / len(rates) for pattern, rates in patterns.items()
            }
            for model, patterns in effectiveness.items()
        }

    def analyze_model_progression(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze how models progress through difficulties and handle concepts.

        Returns:
            Dictionary containing progression analysis for each model
        """
        progression = {}
        difficulty_order = ["very easy", "easy", "medium", "hard", "very hard"]

        for model_name in self.models:
            model_stats = {
                "capability_level": {
                    "total_combinations": 0,
                    "difficulty_distribution": defaultdict(int),
                    "difficulty_percentage": {},  # % of tasks at each difficulty
                },
                "performance_by_difficulty": defaultdict(
                    lambda: {
                        "success_rate": 0.0,
                        "num_combinations": 0,
                        "concepts": defaultdict(
                            int
                        ),  # concepts attempted at this difficulty
                        "successful_patterns": defaultdict(
                            int
                        ),  # patterns used in successful attempts
                        "failed_patterns": defaultdict(
                            int
                        ),  # patterns used in failed attempts
                    }
                ),
                "concept_progression": defaultdict(
                    lambda: {
                        "difficulties_reached": set(),
                        "success_by_difficulty": defaultdict(float),
                        "patterns_by_difficulty": defaultdict(lambda: defaultdict(int)),
                    }
                ),
            }

            # Analyze each combination this model attempted
            for combo in self.concept_combinations.values():
                if model_name not in combo.model_performances:
                    continue

                perf = combo.model_performances[model_name]
                difficulty = combo.difficulty

                # Update capability level stats
                model_stats["capability_level"]["total_combinations"] += 1
                model_stats["capability_level"]["difficulty_distribution"][
                    difficulty
                ] += 1

                # Update performance for this difficulty
                diff_stats = model_stats["performance_by_difficulty"][difficulty]
                diff_stats["num_combinations"] += 1
                diff_stats["success_rate"] = (
                    diff_stats["success_rate"] * (diff_stats["num_combinations"] - 1)
                    + perf["success_rate"]
                ) / diff_stats["num_combinations"]

                # Track concepts and patterns at this difficulty
                for concept in combo.concepts:
                    diff_stats["concepts"][concept] += 1

                    # Update concept progression
                    concept_prog = model_stats["concept_progression"][concept]
                    concept_prog["difficulties_reached"].add(difficulty)

                    # Track success rate for this concept at this difficulty
                    current_rate = concept_prog["success_by_difficulty"][difficulty]
                    current_count = len(concept_prog["difficulties_reached"])
                    concept_prog["success_by_difficulty"][difficulty] = (
                        current_rate * (current_count - 1) + perf["success_rate"]
                    ) / current_count

                    # Track patterns used for this concept at this difficulty
                    for pattern, freq in perf["patterns"].items():
                        if perf["success_rate"] > 0:
                            diff_stats["successful_patterns"][pattern] += 1
                            concept_prog["patterns_by_difficulty"][difficulty][
                                pattern
                            ] += 1
                        else:
                            diff_stats["failed_patterns"][pattern] += 1

            # Calculate percentages for difficulty distribution
            total = model_stats["capability_level"]["total_combinations"]
            model_stats["capability_level"]["difficulty_percentage"] = {
                diff: (count / total * 100)
                for diff, count in model_stats["capability_level"][
                    "difficulty_distribution"
                ].items()
            }

            # Sort difficulties by the defined order
            model_stats["performance_by_difficulty"] = dict(
                sorted(
                    model_stats["performance_by_difficulty"].items(),
                    key=lambda x: (
                        difficulty_order.index(x[0]) if x[0] in difficulty_order else -1
                    ),
                )
            )

            progression[model_name] = model_stats

        return progression

    def print_progression_analysis(self, progression: Dict[str, Dict[str, Any]]):
        """Print a detailed analysis of model progression."""
        for model_name, stats in progression.items():
            print(f"\n=== {model_name} Capability Analysis ===")

            # 1. Capability Level
            print("\nCapability Level (Difficulty Distribution):")
            for diff, percentage in stats["capability_level"][
                "difficulty_percentage"
            ].items():
                count = stats["capability_level"]["difficulty_distribution"][diff]
                print(f"  {diff}: {count} tasks ({percentage:.1f}%)")

            # 2. Performance Progression
            print("\nPerformance Progression:")
            for diff, perf in stats["performance_by_difficulty"].items():
                print(f"\n  {diff} Difficulty:")
                print(f"    Success Rate: {perf['success_rate']:.2f}")
                print(f"    Number of Combinations: {perf['num_combinations']}")

                # Show top concepts at this difficulty
                print("    Top Concepts:")
                for concept, count in sorted(
                    perf["concepts"].items(), key=lambda x: x[1], reverse=True
                )[:3]:
                    print(f"      {concept}: {count} combinations")

                # Show most successful patterns
                if perf["successful_patterns"]:
                    print("    Most Successful Patterns:")
                    for pattern, count in sorted(
                        perf["successful_patterns"].items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:3]:
                        print(f"      {pattern}: {count} successes")

            # 3. Concept Progression
            print("\nConcept Progression Highlights:")
            for concept, prog in stats["concept_progression"].items():
                if len(prog["difficulties_reached"]) > 1:  # Show concepts that progress
                    print(f"\n  {concept}:")
                    print(
                        f"    Difficulties Reached: {sorted(prog['difficulties_reached'])}"
                    )
                    print("    Success Rates:")
                    for diff, rate in sorted(
                        prog["success_by_difficulty"].items(),
                        key=lambda x: x[1],
                        reverse=True,
                    ):
                        print(f"      {diff}: {rate:.2f}")

                    # Show top patterns for most difficult level reached
                    max_diff = max(
                        prog["difficulties_reached"],
                        key=lambda x: [
                            "very easy",
                            "easy",
                            "medium",
                            "hard",
                            "very hard",
                        ].index(x),
                    )
                    print(f"    Top Patterns at {max_diff}:")
                    patterns = prog["patterns_by_difficulty"][max_diff]
                    for pattern, count in sorted(
                        patterns.items(), key=lambda x: x[1], reverse=True
                    )[:3]:
                        print(f"      {pattern}: {count} uses")

    def analyze_pattern_insights(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze pattern usage and effectiveness in relation to model capabilities.

        This analysis focuses on:
        1. How patterns correlate with success at different difficulty levels
        2. Pattern progression across difficulty levels
        3. Pattern effectiveness for specific concept combinations
        """
        insights = {}
        difficulty_order = ["very easy", "easy", "medium", "hard", "very hard"]

        for model_name in self.models:
            model_insights = {
                "pattern_progression": defaultdict(
                    lambda: {
                        "usage_by_difficulty": defaultdict(int),
                        "success_by_difficulty": defaultdict(list),
                        "concept_correlation": defaultdict(list),
                    }
                ),
                "successful_patterns": defaultdict(
                    lambda: {
                        "success_count": 0,
                        "total_usage": 0,
                        "effective_concepts": defaultdict(float),
                        "difficulty_distribution": defaultdict(int),
                    }
                ),
                "failed_patterns": defaultdict(
                    lambda: {
                        "failure_count": 0,
                        "total_usage": 0,
                        "problematic_concepts": defaultdict(float),
                        "difficulty_distribution": defaultdict(int),
                    }
                ),
            }

            # Analyze each combination
            for combo in self.concept_combinations.values():
                if model_name not in combo.model_performances:
                    continue

                perf = combo.model_performances[model_name]
                difficulty = combo.difficulty
                success_rate = perf["success_rate"]

                # Analyze each pattern's usage and effectiveness
                for pattern, frequency in perf["patterns"].items():
                    # Track pattern progression
                    prog = model_insights["pattern_progression"][pattern]
                    prog["usage_by_difficulty"][difficulty] += 1
                    prog["success_by_difficulty"][difficulty].append(success_rate)

                    # Track pattern success/failure
                    if success_rate > 0:
                        success_data = model_insights["successful_patterns"][pattern]
                        success_data["success_count"] += 1
                        success_data["total_usage"] += 1
                        success_data["difficulty_distribution"][difficulty] += 1

                        # Track which concepts this pattern works well with
                        for concept in combo.concepts:
                            current = success_data["effective_concepts"][concept]
                            success_data["effective_concepts"][concept] = (
                                (current + success_rate) / 2
                                if current > 0
                                else success_rate
                            )
                    else:
                        failure_data = model_insights["failed_patterns"][pattern]
                        failure_data["failure_count"] += 1
                        failure_data["total_usage"] += 1
                        failure_data["difficulty_distribution"][difficulty] += 1

                        # Track which concepts this pattern struggles with
                        for concept in combo.concepts:
                            failure_data["problematic_concepts"][concept] += 1

                    # Track concept correlations
                    for concept in combo.concepts:
                        prog["concept_correlation"][concept].append(success_rate)

            # Calculate final metrics
            pattern_metrics = {
                "by_difficulty": defaultdict(
                    lambda: {"top_patterns": [], "success_rates": defaultdict(float)}
                ),
                "overall_effectiveness": {},
                "concept_specialization": defaultdict(list),
            }

            # Analyze pattern progression by difficulty
            for pattern, prog in model_insights["pattern_progression"].items():
                for diff in difficulty_order:
                    if (
                        diff in prog["success_by_difficulty"]
                        and prog["success_by_difficulty"][diff]
                    ):
                        avg_success = sum(prog["success_by_difficulty"][diff]) / len(
                            prog["success_by_difficulty"][diff]
                        )
                        pattern_metrics["by_difficulty"][diff]["success_rates"][
                            pattern
                        ] = avg_success

            # Calculate concept correlations
            for concept, rates in prog["concept_correlation"].items():
                if len(rates) > 1:  # Need at least 2 points for correlation
                    avg_success = sum(rates) / len(rates)
                    if avg_success > 0:  # Only track positive correlations
                        pattern_metrics["concept_specialization"][concept].append(
                            (pattern, avg_success)
                        )

            # Sort and finalize metrics
            for diff in difficulty_order:
                diff_data = pattern_metrics["by_difficulty"][diff]
                sorted_patterns = sorted(
                    diff_data["success_rates"].items(), key=lambda x: x[1], reverse=True
                )
                diff_data["top_patterns"] = sorted_patterns[
                    :5
                ]  # Top 5 patterns per difficulty

            # Calculate overall pattern effectiveness
            all_patterns = set(model_insights["successful_patterns"].keys()) | set(
                model_insights["failed_patterns"].keys()
            )
            pattern_metrics["overall_effectiveness"] = {
                pattern: {
                    "success_rate": (
                        model_insights["successful_patterns"][pattern]["success_count"]
                        / (
                            model_insights["successful_patterns"][pattern][
                                "total_usage"
                            ]
                            + model_insights["failed_patterns"][pattern]["total_usage"]
                        )
                        if pattern in model_insights["successful_patterns"]
                        else 0
                    ),
                    "usage_count": (
                        model_insights["successful_patterns"][pattern]["total_usage"]
                        + model_insights["failed_patterns"][pattern]["total_usage"]
                    ),
                    "difficulty_coverage": (
                        len(
                            set(
                                model_insights["successful_patterns"][pattern][
                                    "difficulty_distribution"
                                ].keys()
                                | model_insights["failed_patterns"][pattern][
                                    "difficulty_distribution"
                                ].keys()
                            )
                        )
                        if pattern in model_insights["successful_patterns"]
                        or pattern in model_insights["failed_patterns"]
                        else 0
                    ),
                }
                for pattern in all_patterns
            }

            # Sort concept specializations
            pattern_metrics["concept_specialization"] = {
                concept: sorted(patterns, key=lambda x: x[1], reverse=True)[
                    :3
                ]  # Top 3 patterns per concept
                for concept, patterns in pattern_metrics[
                    "concept_specialization"
                ].items()
            }

            insights[model_name] = pattern_metrics

        return insights

    def analyze_pattern_concept_correlations(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze how patterns correlate with specific concepts and their success ratios.

        Returns:
            Dictionary containing:
            - For each model:
                - For each concept:
                    - Patterns used (with frequency and success rates)
                    - Most successful patterns
                    - Pattern effectiveness by difficulty
        """
        correlations = {}

        for model_name in self.models:
            concept_patterns = defaultdict(
                lambda: {
                    "patterns": defaultdict(
                        lambda: {
                            "usage_count": 0,
                            "success_count": 0,
                            "by_difficulty": defaultdict(
                                lambda: {"usage_count": 0, "success_count": 0}
                            ),
                        }
                    )
                }
            )

            # Analyze each combination for this model
            for combo in self.concept_combinations.values():
                if model_name not in combo.model_performances:
                    continue

                perf = combo.model_performances[model_name]
                success = perf["success_rate"]
                difficulty = combo.difficulty

                # For each concept in this combination
                for concept in combo.concepts:
                    # For each pattern used
                    for pattern, frequency in perf["patterns"].items():
                        pattern_stats = concept_patterns[concept]["patterns"][pattern]
                        pattern_stats["usage_count"] += 1
                        pattern_stats["success_count"] += success

                        # Track by difficulty
                        diff_stats = pattern_stats["by_difficulty"][difficulty]
                        diff_stats["usage_count"] += 1
                        diff_stats["success_count"] += success

            # Calculate success ratios and compile insights
            model_correlations = {}
            for concept, data in concept_patterns.items():
                pattern_insights = []

                for pattern, stats in data["patterns"].items():
                    success_ratio = (
                        stats["success_count"] / stats["usage_count"]
                        if stats["usage_count"] > 0
                        else 0
                    )

                    # Calculate success ratio by difficulty
                    difficulty_insights = {}
                    for diff, diff_stats in stats["by_difficulty"].items():
                        diff_success_ratio = (
                            diff_stats["success_count"] / diff_stats["usage_count"]
                            if diff_stats["usage_count"] > 0
                            else 0
                        )
                        difficulty_insights[diff] = {
                            "usage_count": diff_stats["usage_count"],
                            "success_ratio": diff_success_ratio,
                        }

                    pattern_insights.append(
                        {
                            "pattern": pattern,
                            "usage_count": stats["usage_count"],
                            "success_ratio": success_ratio,
                            "by_difficulty": difficulty_insights,
                        }
                    )

                # Sort patterns by success ratio (for patterns used more than once)
                significant_patterns = [
                    p for p in pattern_insights if p["usage_count"] > 1
                ]
                sorted_patterns = sorted(
                    significant_patterns,
                    key=lambda x: (x["success_ratio"], x["usage_count"]),
                    reverse=True,
                )

                model_correlations[concept] = {
                    "total_patterns": len(data["patterns"]),
                    "pattern_insights": sorted_patterns,
                    "difficulty_distribution": self._get_difficulty_distribution(
                        concept, model_name
                    ),
                }

            correlations[model_name] = model_correlations

        return correlations

    def _get_difficulty_distribution(
        self, concept: str, model_name: str
    ) -> Dict[str, int]:
        """Helper method to get difficulty distribution for a concept."""
        distribution = defaultdict(int)
        for combo in self.concept_combinations.values():
            if model_name in combo.model_performances and concept in combo.concepts:
                distribution[combo.difficulty] += 1
        return dict(distribution)


def convert_sets_to_lists(obj):
    """Convert any sets in the object to lists for JSON serialization."""
    if isinstance(obj, dict):
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(item) for item in obj]
    elif isinstance(obj, set):
        return list(obj)
    return obj


def main():
    """Main function to run the comparative analysis."""
    analyzer = ComparativeAnalyzer("analysis_results/phase_3_pattern_analysis.json")

    # Get analyses
    progression = analyzer.analyze_model_progression()
    pattern_insights = analyzer.analyze_pattern_insights()
    concept_correlations = analyzer.analyze_pattern_concept_correlations()

    # Print progression analysis
    analyzer.print_progression_analysis(progression)

    # Print pattern insights
    print("\n=== Pattern Analysis ===")
    for model_name, insights in pattern_insights.items():
        print(f"\n{model_name} Pattern Insights:")

        print("\nTop Patterns by Difficulty:")
        for diff in ["very easy", "easy", "medium", "hard", "very hard"]:
            if diff in insights["by_difficulty"]:
                print(f"\n  {diff}:")
                for pattern, success_rate in insights["by_difficulty"][diff][
                    "top_patterns"
                ]:
                    print(f"    {pattern}: {success_rate:.2f} success rate")

        print("\nMost Effective Patterns Overall:")
        sorted_patterns = sorted(
            insights["overall_effectiveness"].items(),
            key=lambda x: (x[1]["success_rate"], x[1]["usage_count"]),
            reverse=True,
        )[:5]
        for pattern, stats in sorted_patterns:
            print(f"  {pattern}:")
            print(f"    Success Rate: {stats['success_rate']:.2f}")
            print(f"    Usage Count: {stats['usage_count']}")
            print(f"    Difficulty Coverage: {stats['difficulty_coverage']} levels")

    # Print concept-pattern correlations
    print("\n=== Concept-Pattern Correlations ===")
    for model_name, correlations in concept_correlations.items():
        print(f"\n{model_name} Concept Correlations:")

        for concept, data in correlations.items():
            print(f"\n  {concept}:")
            print(f"    Total Patterns Used: {data['total_patterns']}")
            print("    Difficulty Distribution:")
            for diff, count in data["difficulty_distribution"].items():
                print(f"      {diff}: {count} tasks")

            print("    Most Successful Patterns:")
            for pattern in data["pattern_insights"]:
                print(f"      {pattern['pattern']}:")
                print(f"        Usage Count: {pattern['usage_count']}")
                print(f"        Success Ratio: {pattern['success_ratio']:.2f}")
                print("        Performance by Difficulty:")
                for diff, stats in pattern["by_difficulty"].items():
                    if stats["usage_count"] > 0:
                        print(
                            f"          {diff}: {stats['success_ratio']:.2f} success rate ({stats['usage_count']} uses)"
                        )

    # Save detailed analysis to file
    output = {
        "model_progression": convert_sets_to_lists(progression),
        "pattern_insights": convert_sets_to_lists(pattern_insights),
        "concept_pattern_correlations": convert_sets_to_lists(concept_correlations),
        "concept_difficulty_matrix": analyzer.get_concept_difficulty_matrix(),
        "pattern_effectiveness": analyzer.get_pattern_effectiveness(),
    }

    output_file = "analysis_results/comparative_analysis.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDetailed analysis saved to: {output_file}")


if __name__ == "__main__":
    main()
