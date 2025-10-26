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


class PatternVisualizationGenerator:
    """Generates visualizations for solution pattern metrics"""

    def __init__(self, output_dir: Path):
        """Initialize generator with output directory"""
        self.output_dir = output_dir
        self.pattern_metrics_dir = output_dir / "pattern_metrics"
        self.pattern_metrics_dir.mkdir(exist_ok=True, parents=True)

    def generate_visualizations(self, metrics: dict):
        """Generate all solution pattern visualizations"""
        self._visualize_pattern_distributions(metrics)
        self._visualize_pattern_heatmap(metrics)
        self._visualize_pattern_by_difficulty(metrics)

    def _visualize_pattern_distributions(self, metrics: dict):
        """Generate pattern distribution visualization"""
        data = []
        for concept_key, pattern_types in metrics["pattern_distributions"].items():
            for pattern_type, count in pattern_types.items():
                data.append(
                    {
                        "Concept Combination": concept_key,
                        "Pattern Type": pattern_type,
                        "Count": count,
                    }
                )

        df = pd.DataFrame(data)
        if not df.empty:
            plt.figure(figsize=(15, 8))
            pivot_table = df.pivot_table(
                values="Count",
                index="Concept Combination",
                columns="Pattern Type",
                fill_value=0,
            )
            sns.heatmap(pivot_table, annot=True, cmap="YlOrRd", fmt="g")
            plt.title("Solution Pattern Distribution Across Concept Combinations")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(self.pattern_metrics_dir / "pattern_distributions.png")
            plt.close()

    def _visualize_pattern_heatmap(self, metrics: dict):
        """Generate pattern usage heatmap"""
        data = []
        for group_key, group_metrics in metrics["comparative_analysis"].items():
            concepts_and_difficulty = group_key.split("-")
            concepts = concepts_and_difficulty[:-1]  # All but the last element

            for concept in concepts:
                concept = concept_names.get(concept, concept)

                for pattern_type, count in group_metrics["patterns"].items():
                    data.append(
                        {
                            "Concept": concept,
                            "Pattern Type": pattern_type,
                            "Count": count,
                        }
                    )

        df = pd.DataFrame(data)
        if not df.empty:
            # Create pivot table
            pivot_table = df.pivot_table(
                values="Count",
                index="Concept",
                columns="Pattern Type",
                fill_value=0,
            )

            # Calculate column sums and get top 15 patterns
            col_sums = pivot_table.sum()
            top_10_patterns = col_sums.nlargest(15).index
            pivot_table = pivot_table[top_10_patterns]

            plt.figure(figsize=(12, 8))
            sns.heatmap(
                pivot_table,
                annot=True,
                cmap="viridis",
                cbar=False,
                annot_kws={"size": 16, "weight": "bold"},
            )
            plt.title(
                "Solution Pattern Distribution (Top 15 Patterns)",
                size=18,
                weight="bold",
            )
            plt.xlabel("Pattern Type", size=16, weight="bold", labelpad=15)
            plt.ylabel("Concept", size=16, weight="bold", labelpad=15)
            plt.xticks(
                rotation=45, ha="right", size=14
            )  # Align x-axis tick marks correctly
            ax = plt.gca()
            ax.set_xticklabels(
                ax.get_xticklabels(), size=14, weight="bold"
            )  # Make x-axis labels bigger
            ax.set_yticklabels(
                ax.get_yticklabels(), size=14, weight="bold"
            )  # Make y-axis labels bigger
            plt.tight_layout()
            plt.savefig(self.pattern_metrics_dir / "pattern_usage_heatmap.png")
            plt.savefig(self.pattern_metrics_dir / "pattern_usage_heatmap.pdf")
            plt.close()

    def _visualize_pattern_by_difficulty(self, metrics: dict):
        """Generate pattern usage by difficulty visualization"""
        data = []
        for group_key, group_metrics in metrics["comparative_analysis"].items():
            concept_key, difficulty = group_key.rsplit("-", 1)
            for category, count in group_metrics["pattern_distribution"].items():
                data.append(
                    {
                        "Difficulty": difficulty,
                        "Pattern Category": category,
                        "Count": count,
                    }
                )

        df = pd.DataFrame(data)
        if not df.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x="Difficulty", y="Count", hue="Pattern Category", data=df)
            plt.title("Solution Pattern Categories by Difficulty Level")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(self.pattern_metrics_dir / "pattern_by_difficulty.png")
            plt.close()


if __name__ == "__main__":
    for model in ["4o", "4o-mini", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]:
        test_visualizer = PatternVisualizationGenerator(
            Path(f"experiments/{model}/average_metrics/phase_3")
        )
        metrics = json.load(
            open(f"experiments/{model}/average_metrics/phase_3/pattern_metrics.json")
        )
        test_visualizer.generate_visualizations(metrics)
