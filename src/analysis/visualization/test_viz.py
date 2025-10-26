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


class TestVisualizationGenerator:
    """Generates visualizations for test validation metrics"""

    def __init__(self, output_dir: Path):
        """Initialize generator with output directory"""
        self.output_dir = output_dir
        self.test_metrics_dir = output_dir / "test_metrics"
        self.test_metrics_dir.mkdir(exist_ok=True, parents=True)

    def generate_visualizations(self, metrics: dict):
        """Generate all test validation visualizations"""
        self._visualize_validation_distributions(metrics)
        self._visualize_validation_heatmap(metrics)
        self._visualize_validation_by_difficulty(metrics)

    def _visualize_validation_distributions(self, metrics: dict):
        """Generate validation issues distribution visualization"""

        def format_validation_issue(issue: str) -> tuple:
            words = issue.split("_")
            if words[0] == "coverage":
                return ("Coverage", " ".join(word.capitalize() for word in words[1:]))
            elif words[0] == "edge":
                return ("Edge Cases", " ".join(word.capitalize() for word in words[1:]))
            elif words[0] == "missing":
                return (
                    "Missing Cases",
                    " ".join(word.capitalize() for word in words[1:]),
                )
            else:
                return ("Other", " ".join(word.capitalize() for word in words))

        data = []
        for concept_key, validation_types in metrics[
            "validation_distributions"
        ].items():
            concept_key = " - ".join(
                concept_names.get(c, c) for c in concept_key.split("-")
            )
            for validation_type, count in validation_types.items():
                if (
                    validation_type != "total_suggestions"
                    and not validation_type.startswith("incorrect")
                ):
                    category, issue = format_validation_issue(validation_type)
                    data.append(
                        {
                            "Concept Combination": concept_key,
                            "Category": category,
                            "Issue": issue,
                            "Count": round(count, 1),
                        }
                    )

        df = pd.DataFrame(data)
        if not df.empty:
            plt.figure(
                figsize=(10, 11)
            )  # Increased figure height to accommodate labels

            # Create hierarchical columns but only use the issue part for the heatmap
            pivot_table = df.pivot_table(
                values="Count",
                index="Concept Combination",
                columns=["Category", "Issue"],
                fill_value=0,
            )

            # Sort columns by category
            categories = [
                "Coverage",
                "Edge Cases",
                "Missing Cases",
                "Other",
            ]
            sorted_cols = []
            for cat in categories:
                cat_cols = [(c, i) for c, i in pivot_table.columns if c == cat]
                sorted_cols.extend(sorted(cat_cols))

            pivot_table = pivot_table[sorted_cols]

            # Create the heatmap
            ax = sns.heatmap(
                pivot_table,
                annot=True,
                cmap="YlOrRd",
                fmt="g",
                cbar=False,
                annot_kws={"size": 18, "weight": "bold"},
            )

            # Format the y-axis (concept combination) labels
            plt.yticks(rotation=0)
            ax.set_yticklabels(ax.get_yticklabels(), size=12)

            # Hide the first level of column labels and adjust issue labels
            ax.xaxis.set_ticklabels([col[1] for col in pivot_table.columns], size=9)
            ax.xaxis.set_label_text("")  # Remove the 'Category, Issue' label
            ax.yaxis.set_label_text("")
            # Add category separators and labels

            current_x = 0
            category_positions = {}

            # First pass: calculate positions and store tuple of (mid_point, start_x, width)
            for category in categories:
                cat_cols = [col for col in pivot_table.columns if col[0] == category]
                if cat_cols:
                    width = len(cat_cols)
                    mid_point = current_x + width / 2
                    category_positions[category] = (mid_point, current_x, width)

                    if current_x > 0:  # Draw separator line
                        plt.axvline(x=current_x, color="white", linewidth=8)

                    current_x += width

            # Add category labels at the top
            ax = plt.gca()
            for category, (mid_point, start_x, width) in category_positions.items():
                # Add text above the plot
                plt.text(
                    mid_point,
                    -0.6,  # Changed from -0.6 to -1.2 to move labels down
                    category,
                    horizontalalignment="center",
                    verticalalignment="top",
                    size=14,
                    weight="bold",
                )

            ax = plt.gca()
            ax.set_xticklabels(
                ax.get_xticklabels(), size=13, weight="bold"
            )  # Make x-axis labels bigger
            ax.set_yticklabels(
                ax.get_yticklabels(), size=12, weight="bold"
            )  # Make y-axis labels bigger
            # Add category labels below the heatmap with more space

            plt.title(
                "Test Validation Issues Distribution", size=18, weight="bold", pad=50
            )  # Changed pad from 30 to 50
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(
                self.test_metrics_dir / "validation_distributions.png",
                bbox_inches="tight",
                pad_inches=0.5,
            )  # Added padding for labels
            plt.savefig(
                self.test_metrics_dir / "validation_distributions.pdf",
                bbox_inches="tight",
                pad_inches=0.5,
            )  # Added padding for labels
            plt.close()

    def _visualize_validation_heatmap(self, metrics: dict):
        """Generate validation pattern heatmap"""
        data = []
        for group_key, group_metrics in metrics["comparative_analysis"].items():
            concept_key = group_key.split("-")[0]
            for issue_type, count in group_metrics["validation_issues"].items():
                data.append(
                    {"Concept": concept_key, "Issue Type": issue_type, "Count": count}
                )

        df = pd.DataFrame(data)
        if not df.empty:
            plt.figure(figsize=(12, 8))
            pivot_table = df.pivot_table(
                values="Count", index="Concept", columns="Issue Type", fill_value=0
            )
            sns.heatmap(pivot_table, annot=True, cmap="viridis")
            plt.title("Test Validation Pattern Heatmap")
            plt.tight_layout()
            plt.savefig(self.test_metrics_dir / "validation_pattern_heatmap.png")
            plt.close()

    def _visualize_validation_by_difficulty(self, metrics: dict):
        """Generate validation issues by difficulty visualization"""
        data = []
        for group_key, group_metrics in metrics["comparative_analysis"].items():
            concept_key, difficulty = group_key.rsplit("-", 1)
            for category, count in group_metrics["validation_distribution"].items():
                data.append(
                    {
                        "Difficulty": difficulty,
                        "Issue Category": category,
                        "Count": count,
                    }
                )

        df = pd.DataFrame(data)
        if not df.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(x="Difficulty", y="Count", hue="Issue Category", data=df)
            plt.title("Test Validation Categories by Difficulty Level")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(self.test_metrics_dir / "validation_by_difficulty.png")
            plt.close()


if __name__ == "__main__":
    for model in ["4o", "4o-mini", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]:
        test_visualizer = TestVisualizationGenerator(
            Path(f"experiments/{model}/average_metrics/phase_3")
        )
        metrics = json.load(
            open(f"experiments/{model}/average_metrics/phase_3/test_metrics.json")
        )
        test_visualizer.generate_visualizations(metrics)
