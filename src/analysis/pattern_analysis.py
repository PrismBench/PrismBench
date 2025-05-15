"""
Pattern Analysis Module

This module implements comparative analysis of pattern metrics across different models.
It focuses on standardizing and analyzing concept-difficulty combinations and their associated metrics.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ConceptMetrics:
    """Data class to store standardized metrics for a concept-difficulty combination."""

    concepts: List[str]
    difficulty: str
    success_rate: float
    avg_attempts: float
    patterns: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ConceptMetrics instance to a dictionary."""
        return {
            "concepts": self.concepts,
            "difficulty": self.difficulty,
            "success_rate": self.success_rate,
            "avg_attempts": self.avg_attempts,
            "patterns": self.patterns,
        }

    @classmethod
    def from_key_and_data(cls, key: str, data: Dict[str, Any]) -> "ConceptMetrics":
        """
        Create a ConceptMetrics instance from a concept key and its associated data.

        Args:
            key: String in format "concept1-concept2-...-difficulty"
            data: Dictionary containing metrics data

        Returns:
            ConceptMetrics instance with parsed and standardized data
        """
        parts = key.split("-")
        difficulty = parts[-1]
        concepts = parts[:-1]

        return cls(
            concepts=concepts,
            difficulty=difficulty,
            success_rate=data.get("success_rate", 0.0),
            avg_attempts=data.get("avg_attempts", 0.0),
            patterns=data.get("patterns", {}),
        )


def load_model_metrics(model_name: str) -> Dict[str, ConceptMetrics]:
    """
    Load and standardize metrics for a specific model.

    Args:
        model_name: Name of the model to load metrics for

    Returns:
        Dictionary mapping concept-difficulty combinations to their standardized metrics
    """
    metrics_path = Path(
        f"experiments/{model_name}/average_metrics/phase_3/pattern_metrics.json"
    )

    with open(metrics_path, "r") as f:
        raw_data = json.load(f)

    comparative_data = raw_data.get("comparative_analysis", {})
    standardized_metrics = {}

    for key, data in comparative_data.items():
        metrics = ConceptMetrics.from_key_and_data(key, data)
        standardized_metrics[key] = metrics

    return standardized_metrics


def save_analysis_results(
    model_metrics: Dict[str, Dict[str, ConceptMetrics]], output_path: str
):
    """
    Save the analysis results in a structured JSON format.

    Args:
        model_metrics: Dictionary mapping model names to their metrics
        output_path: Path where to save the JSON file
    """
    output_data = {"models": {}}

    for model_name, metrics in model_metrics.items():
        model_data = {
            "num_combinations": len(metrics),
            "summary": {
                "avg_success_rate": sum(m.success_rate for m in metrics.values())
                / len(metrics),
                "avg_attempts": sum(m.avg_attempts for m in metrics.values())
                / len(metrics),
                "total_patterns": sum(len(m.patterns) for m in metrics.values()),
            },
            "concept_combinations": [],
        }

        # Convert each combination to a flat structure
        for metric in metrics.values():
            combination_data = {
                "concepts": metric.concepts,
                "difficulty": metric.difficulty,
                "success_rate": metric.success_rate,
                "avg_attempts": metric.avg_attempts,
                "patterns": metric.patterns,
            }
            model_data["concept_combinations"].append(combination_data)

        output_data["models"][model_name] = model_data

    # Save to file
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)


def analyze_patterns():
    """Main function to analyze patterns across all models."""
    models = ["4o", "4o-mini", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]
    model_metrics = {}

    # Load and standardize metrics for each model
    for model in models:
        try:
            model_metrics[model] = load_model_metrics(model)
            print(f"\nAnalysis for {model}:")
            print(f"Number of concept combinations: {len(model_metrics[model])}")

            # Show example of concept combinations
            print("\nExample combinations:")
            for i, metric in enumerate(list(model_metrics[model].values())[:3]):
                print(f"\n{i+1}. Concepts: {metric.concepts}")
                print(f"   Difficulty: {metric.difficulty}")
                print(f"   Success Rate: {metric.success_rate:.2f}")
                print(f"   Average Attempts: {metric.avg_attempts:.2f}")
                print(f"   Number of Patterns: {len(metric.patterns)}")
                print(
                    f"   Top Patterns: {', '.join(sorted(metric.patterns.keys())[:3])}"
                )

            # Calculate some basic statistics
            success_rates = [m.success_rate for m in model_metrics[model].values()]
            avg_attempts = [m.avg_attempts for m in model_metrics[model].values()]
            total_patterns = sum(len(m.patterns) for m in model_metrics[model].values())

            print("\nModel Statistics:")
            print(
                f"   Average Success Rate: {sum(success_rates)/len(success_rates):.2f}"
            )
            print(f"   Average Attempts: {sum(avg_attempts)/len(avg_attempts):.2f}")
            print(f"   Total Unique Patterns: {total_patterns}")

        except Exception as e:
            print(f"Error loading metrics for {model}: {str(e)}")

    # Save results to JSON
    output_path = "analysis_results/phase_3_pattern_analysis.json"
    Path("analysis_results").mkdir(exist_ok=True)
    save_analysis_results(model_metrics, output_path)
    print(f"\nAnalysis results saved to: {output_path}")

    return model_metrics


if __name__ == "__main__":
    analyze_patterns()
