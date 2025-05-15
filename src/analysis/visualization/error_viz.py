from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import json

concept_names = {
    "loops": "Loops",
    "conditionals": "Conditionals",
    "functions": "Functions",
    "data_structures": "Data Struct.",
    "algorithms": "Algorithms",
    "error_handling": "Error Hand.",
    "recursion": "Recursion",
    "sorting": "Sorting",
    "searching": "Searching",
    "dynamic_programming": "Dyn. Prog.",
}


def format_error_type(error_type: str) -> str:
    return " ".join(word.capitalize() for word in error_type.split("_"))


class ErrorVisualizationGenerator:
    """Generates visualizations for error metrics"""

    def __init__(self, output_dir: Path):
        """Initialize generator with output directory"""
        self.output_dir = output_dir
        self.error_metrics_dir = output_dir / "error_metrics"
        self.error_metrics_dir.mkdir(exist_ok=True, parents=True)

    def generate_visualizations(self, metrics: dict):
        """Generate all error metrics visualizations"""
        self._visualize_error_distributions(metrics)
        self._visualize_error_heatmap(metrics)
        self._visualize_error_by_difficulty(metrics)

    def _visualize_error_distributions(self, metrics: dict):
        """Generate error distributions visualization"""
        data = []
        for concept_key, error_types in metrics["error_distributions"].items():
            concept_key = "-".join(
                concept_names.get(c, c) for c in concept_key.split("-")
            )
            for error_type, count in error_types.items():
                data.append(
                    {
                        "Concept Combination": concept_key,
                        "Error Type": format_error_type(error_type),
                        "Count": count,
                    }
                )

        df = pd.DataFrame(data)
        if not df.empty:
            pivot_table = df.pivot_table(
                values="Count",
                index="Concept Combination",
                columns="Error Type",
                fill_value=0,
            )

            plt.figure(figsize=(15, 8))
            sns.heatmap(pivot_table, annot=True, cmap="YlOrRd", fmt="g")
            plt.title(
                "Error Distribution Across Concept Combinations", size=18, weight="bold"
            )
            plt.xlabel("Error Type", size=16, weight="bold", labelpad=15)
            plt.ylabel("Concept Combination", size=16, weight="bold", labelpad=15)
            plt.xticks(rotation=45, size=14)
            plt.yticks(rotation=0, size=14)  # Make y-axis labels horizontal
            plt.tight_layout()
            plt.savefig(self.error_metrics_dir / "error_distributions.png")
            plt.close()

    def _visualize_error_heatmap(self, metrics: dict):
        """Generate error pattern heatmap"""
        data = []
        for group_key, group_metrics in metrics["comparative_analysis"].items():
            # Split by difficulty level
            concepts_and_difficulty = group_key.split("-")
            concepts = concepts_and_difficulty[:-1]  # All but the last element

            # Process each concept in the combination
            for concept in concepts:
                concept = concept_names.get(concept, concept)
                for error_type, count in group_metrics["error_patterns"].items():
                    if not (
                        error_type.startswith("fix_") or error_type.startswith("root_")
                    ):
                        data.append(
                            {
                                "Concept": concept,
                                "Error Type": format_error_type(error_type),
                                # Divide count by number of concepts to avoid over-counting
                                "Count": round(count, 1),
                            }
                        )

        df = pd.DataFrame(data)
        if not df.empty:
            plt.figure(figsize=(10, 7))
            # Group by concept and error type, taking the mean in case of duplicates
            pivot_table = df.pivot_table(
                values="Count",
                index="Concept",
                columns="Error Type",
                fill_value=0,
                aggfunc="mean",
            )
            sns.heatmap(
                pivot_table,
                annot=True,
                cmap="viridis",
                fmt=".1f",
                cbar=False,
                annot_kws={"size": 16, "weight": "bold"},
            )  # Make numbers bold and bigger
            plt.title("Error Pattern Distribution", size=18, weight="bold")
            plt.xlabel("Error Type", size=16, weight="bold", labelpad=15)
            plt.ylabel("Concept", size=16, weight="bold", labelpad=15)
            plt.xticks(
                rotation=45, ha="right", size=14
            )  # Align x-axis tick marks correctly
            plt.yticks(rotation=0, size=14)  # Make y-axis labels horizontal
            ax = plt.gca()
            ax.set_xticklabels(
                ax.get_xticklabels(), size=14, weight="bold"
            )  # Make x-axis labels bigger
            ax.set_yticklabels(
                ax.get_yticklabels(), size=14, weight="bold"
            )  # Make y-axis labels bigger
            plt.tight_layout()
            plt.savefig(self.error_metrics_dir / "error_pattern_heatmap.png")
            plt.savefig(self.error_metrics_dir / "error_pattern_heatmap.pdf")
            plt.close()

    def _visualize_error_by_difficulty(self, metrics: dict):
        """Generate error by difficulty visualization"""
        data = []
        for group_key, group_metrics in metrics["comparative_analysis"].items():
            concept_key, difficulty = group_key.rsplit("-", 1)
            concept_key = concept_names.get(concept_key, concept_key)
            for category, count in group_metrics["error_distribution"].items():
                data.append(
                    {
                        "Difficulty": difficulty,
                        "Error Category": format_error_type(category),
                        "Count": count,
                    }
                )

        df = pd.DataFrame(data)
        if not df.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x="Difficulty", y="Count", hue="Error Category", data=df)
            plt.title("Error Categories by Difficulty Level", size=18, weight="bold")
            plt.xlabel("Difficulty", size=16, weight="bold", labelpad=15)
            plt.ylabel("Count", size=16, weight="bold", labelpad=15)
            plt.xticks(rotation=45, size=14)
            plt.yticks(rotation=0, size=14)  # Make y-axis labels horizontal
            plt.tight_layout()
            plt.savefig(self.error_metrics_dir / "error_by_difficulty.png")
            plt.close()


if __name__ == "__main__":
    for model in ["4o", "4o-mini", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]:
        test_visualizer = ErrorVisualizationGenerator(
            Path(f"experiments/{model}/average_metrics/phase_3")
        )
        metrics = json.load(
            open(f"experiments/{model}/average_metrics/phase_3/error_metrics.json")
        )
        test_visualizer.generate_visualizations(metrics)
