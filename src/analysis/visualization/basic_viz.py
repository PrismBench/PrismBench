from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class BasicVisualizationGenerator:
    """Generates visualizations for basic performance metrics"""

    def __init__(self, output_dir: Path):
        """Initialize generator with output directory"""
        self.output_dir = output_dir
        self.basic_metrics_dir = output_dir / "basic_metrics"
        self.basic_metrics_dir.mkdir(exist_ok=True, parents=True)

    def generate_visualizations(self, metrics: dict):
        """Generate all basic performance visualizations"""
        self._visualize_success_rates(metrics)
        self._visualize_average_attempts(metrics)
        self._visualize_fixer_interventions(metrics)
        self._visualize_composite_performance(metrics)
        self.generate_combined_pdf_report(metrics)  # Add this line

    def _visualize_success_rates(self, metrics: dict):
        """Generate success rates visualizations"""
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        sns.barplot(
            x=list(metrics["success_rates_by_concept"].keys()),
            y=list(metrics["success_rates_by_concept"].values()),
        )
        plt.title("Success Rates by Concept")
        plt.xticks(rotation=45)
        plt.ylabel("Success Rate")

        plt.subplot(2, 1, 2)
        difficulties = list(metrics["success_rates_by_difficulty"].keys())
        success_rates = list(metrics["success_rates_by_difficulty"].values())
        sns.barplot(x=difficulties, y=success_rates, palette="viridis")
        plt.title("Success Rates by Difficulty")
        plt.ylabel("Success Rate")
        plt.tight_layout()
        plt.savefig(self.basic_metrics_dir / "success_rates.png")
        plt.close()

    def _visualize_average_attempts(self, metrics: dict):
        """Generate average attempts visualizations"""
        plt.figure(figsize=(10, 6))
        avg_attempts_data_concept = pd.DataFrame(
            {
                "Concept": list(metrics["avg_attempts_by_concept"].keys()),
                "Average Attempts": list(metrics["avg_attempts_by_concept"].values()),
            }
        )
        sns.barplot(
            data=avg_attempts_data_concept,
            x="Concept",
            y="Average Attempts",
            palette="rocket",
        )
        plt.title("Average Attempts by Concept")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.basic_metrics_dir / "average_attempts_concept.png")
        plt.close()

        plt.figure(figsize=(10, 6))
        avg_attempts_data_difficulty = pd.DataFrame(
            {
                "Difficulty": list(metrics["avg_attempts_by_difficulty"].keys()),
                "Average Attempts": list(
                    metrics["avg_attempts_by_difficulty"].values()
                ),
            }
        )
        sns.barplot(
            data=avg_attempts_data_difficulty,
            x="Difficulty",
            y="Average Attempts",
            palette="rocket",
        )
        plt.title("Average Attempts by Difficulty")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.basic_metrics_dir / "average_attempts_difficulty.png")
        plt.close()

    def _visualize_fixer_interventions(self, metrics: dict):
        """Generate fixer interventions visualizations"""
        if metrics["fixer_intervention_rate_difficulty"]:
            plt.figure(figsize=(10, 6))
            difficulties = list(metrics["fixer_intervention_rate_difficulty"].keys())
            interventions = list(metrics["fixer_intervention_rate_difficulty"].values())

            intervention_data = pd.DataFrame(
                {"Difficulty": difficulties, "Interventions": interventions}
            )

            sns.barplot(
                data=intervention_data,
                x="Difficulty",
                y="Interventions",
                palette="Set3",
            )
            plt.title("Problem Fixer Interventions by Difficulty")
            plt.xticks(rotation=45)
            plt.ylabel("Number of Interventions")
            plt.tight_layout()
            plt.savefig(self.basic_metrics_dir / "fixer_interventions_difficulty.png")
            plt.close()

        if metrics["fixer_intervention_rate_concept"]:
            plt.figure(figsize=(10, 6))
            concepts = list(metrics["fixer_intervention_rate_concept"].keys())
            interventions = list(metrics["fixer_intervention_rate_concept"].values())

            intervention_data = pd.DataFrame(
                {"Concept": concepts, "Interventions": interventions}
            )

            sns.barplot(
                data=intervention_data,
                x="Concept",
                y="Interventions",
                palette="Set3",
            )
            plt.title("Problem Fixer Interventions by Concept")
            plt.xticks(rotation=45)
            plt.ylabel("Number of Interventions")
            plt.tight_layout()
            plt.savefig(self.basic_metrics_dir / "fixer_interventions_concepts.png")
            plt.close()

    def _visualize_composite_performance(self, metrics: dict):
        """Generate composite performance visualizations"""
        # Composite view by difficulty
        plt.figure(figsize=(15, 8))
        diff_levels = list(metrics["success_rates_by_difficulty"].keys())
        success_rates = list(metrics["success_rates_by_difficulty"].values())
        avg_attempts = [
            metrics["avg_attempts_by_difficulty"].get(d, 0) for d in diff_levels
        ]
        interventions = [
            metrics["fixer_intervention_rate_difficulty"].get(d, 0) for d in diff_levels
        ]

        x = np.arange(len(diff_levels))
        width = 0.25

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()

        # Plot success rates and average attempts on primary axis
        ax1.bar(
            x - width / 2,
            success_rates,
            width,
            label="Success Rate",
            color="skyblue",
        )
        ax1.bar(
            x + width / 2,
            avg_attempts,
            width,
            label="Avg Attempts",
            color="lightgreen",
        )

        # Plot interventions on secondary axis
        ax2.plot(x, interventions, "r-", marker="o", label="Interventions")

        ax1.set_xlabel("Difficulty Level")
        ax1.set_ylabel("Rate / Attempts")
        ax2.set_ylabel("Interventions")

        ax1.set_xticks(x)
        ax1.set_xticklabels(diff_levels, rotation=45)

        # Add legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        plt.title("Composite Performance Metrics by Difficulty")
        plt.tight_layout()
        plt.savefig(self.basic_metrics_dir / "composite_performance_difficulty.png")
        plt.close()

        # Composite view by concept
        plt.figure(figsize=(15, 8))
        concepts = list(metrics["success_rates_by_concept"].keys())
        success_rates = list(metrics["success_rates_by_concept"].values())
        avg_attempts = [metrics["avg_attempts_by_concept"].get(c, 0) for c in concepts]
        interventions = [
            metrics["fixer_intervention_rate_concept"].get(c, 0) for c in concepts
        ]

        x = np.arange(len(concepts))
        width = 0.25

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()

        # Plot success rates and average attempts on primary axis
        ax1.bar(
            x - width / 2,
            success_rates,
            width,
            label="Success Rate",
            color="skyblue",
        )
        ax1.bar(
            x + width / 2,
            avg_attempts,
            width,
            label="Avg Attempts",
            color="lightgreen",
        )

        # Plot interventions on secondary axis
        ax2.plot(x, interventions, "r-", marker="o", label="Interventions")

        ax1.set_xlabel("Concepts")
        ax1.set_ylabel("Rate / Attempts")
        ax2.set_ylabel("Interventions")

        ax1.set_xticks(x)
        ax1.set_xticklabels(concepts, rotation=45)

        # Add legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        plt.title("Composite Performance Metrics by Concept")
        plt.tight_layout()
        plt.savefig(self.basic_metrics_dir / "composite_performance_concept.png")
        plt.close()

    def generate_combined_pdf_report(self, metrics: dict):
        """Generate a PDF report with 2 key visualizations in a grid"""
        # Set up publication-quality styling
        plt.style.use("seaborn-v0_8-paper")
        plt.rcParams.update(
            {
                "font.family": "serif",
                "axes.linewidth": 1.2,
                "axes.edgecolor": "#333333",
                "grid.alpha": 0.2,
                "font.size": 16,
                "axes.labelsize": 20,
                "axes.titlesize": 22,
                "legend.fontsize": 16,
                "legend.frameon": True,
                "legend.framealpha": 0.9,
                "legend.edgecolor": "#333333",
            }
        )

        concept_display_names = {
            "loops": "Loops",
            "dynamic_programming": "Dyn. Prog.",
            "recursion": "Recursion",
            "algorithms": "Algorithms",
            "data_structures": "Data Struct.",
            "conditionals": "Conditionals",
            "error_handling": "Error Hand.",
            "sorting": "Sorting",
            "searching": "Searching",
        }

        fig = plt.figure(figsize=(30, 8))
        main_gs = fig.add_gridspec(
            1, 3, hspace=0.5, wspace=0.5, width_ratios=[0.01, 1, 1]
        )

        # Composite performance by difficulty
        ax_composite_diff = fig.add_subplot(main_gs[0, 1])

        difficulties = list(metrics["success_rates_by_difficulty"].keys())
        x = np.arange(len(difficulties))
        width = 0.25

        # Plot bars with enhanced styling
        ax_composite_diff.bar(
            x - width / 2,
            list(metrics["success_rates_by_difficulty"].values()),
            width,
            label="Success Rate",
            color="#2ca02c",
            zorder=3,
        )  # Green color
        ax_composite_diff.bar(
            x + width / 2,
            [metrics["avg_attempts_by_difficulty"].get(d, 0) for d in difficulties],
            width,
            label="Avg Attempts",
            color="#9467bd",
            zorder=3,
        )  # Purple color

        # Style the composite plot
        ax_composite_diff.set_xlabel("Difficulty Level", fontweight="bold")
        ax_composite_diff.set_ylabel("Rate / Attempts", fontweight="bold")
        ax_composite_diff.set_xticks(x)
        ax_composite_diff.set_xticklabels(
            difficulties, rotation=45, ha="right", fontsize=16
        )
        ax_composite_diff.grid(True, linestyle="--", alpha=0.3, zorder=0)
        ax_composite_diff.spines["top"].set_visible(False)
        ax_composite_diff.set_title(
            "Composite Performance by Difficulty", pad=20, fontweight="bold"
        )

        # Composite performance by concept
        ax_composite_concept = fig.add_subplot(main_gs[0, 2])
        ax2_concept = ax_composite_concept.twinx()

        concepts = list(metrics["success_rates_by_concept"].keys())
        x = np.arange(len(concepts))
        width = 0.25

        # Plot bars and line with enhanced styling
        ax_composite_concept.bar(
            x - width / 2,
            list(metrics["success_rates_by_concept"].values()),
            width,
            label="Success Rate",
            color="#2ca02c",
            zorder=3,
        )  # Green color
        ax_composite_concept.bar(
            x + width / 2,
            [metrics["avg_attempts_by_concept"].get(c, 0) for c in concepts],
            width,
            label="Avg Attempts",
            color="#9467bd",
            zorder=3,
        )  # Purple color
        ax2_concept.plot(
            x,
            [metrics["fixer_intervention_rate_concept"].get(c, 0) for c in concepts],
            "r-",
            marker="o",
            label="Interventions",
            linewidth=2,
            markersize=8,
            zorder=4,
        )

        # Style the composite plot
        ax_composite_concept.set_xlabel("Concepts", fontweight="bold")
        ax_composite_concept.set_ylabel("Rate / Attempts", fontweight="bold")
        ax2_concept.set_ylabel("Interventions", fontweight="bold")
        ax_composite_concept.set_xticks(x)
        ax_composite_concept.set_xticklabels(
            [concept_display_names.get(c, c) for c in concepts],
            rotation=45,
            ha="right",
            fontsize=16,
        )
        ax_composite_concept.grid(True, linestyle="--", alpha=0.3, zorder=0)
        ax_composite_concept.spines["top"].set_visible(False)
        ax_composite_concept.set_title(
            "Composite Performance by Concept", pad=20, fontweight="bold"
        )

        # Add a single legend for both charts
        handles = [
            plt.Rectangle((0, 0), 1, 1, fc="#2ca02c", edgecolor="none"),  # Green color
            plt.Rectangle((0, 0), 1, 1, fc="#9467bd", edgecolor="none"),  # Purple color
            plt.Line2D(
                [0],
                [0],
                color="r",
                marker="o",
                linestyle="-",
                linewidth=2,
                markersize=8,
            ),  # Red line
        ]
        labels = ["Success Rate", "Avg Attempts", "Interventions"]
        fig.legend(
            handles,
            labels,
            loc="center",
            bbox_to_anchor=(0.1, 0.5),
            frameon=True,
            fancybox=True,
            shadow=True,
        )

        # Save with high quality settings
        plt.savefig(
            self.basic_metrics_dir / "combined_metrics.pdf",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
            pad_inches=0.3,
        )
        plt.close()


if __name__ == "__main__":
    for model in ["4o", "4o-mini", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]:
        basic_visualizer = BasicVisualizationGenerator(
            Path(f"experiments/{model}/average_metrics/whole_tree")
        )
        metrics = json.load(
            open(f"experiments/{model}/average_metrics/whole_tree/basic_metrics.json")
        )
        basic_visualizer.generate_visualizations(metrics)
