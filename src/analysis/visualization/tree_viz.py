from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import json

models = {
    "4o": "GPT-4o",
    "4o-mini": "GPT-4o-mini",
    "llama3.1-8b": "Llama3.1-8B",
    "llama3.1-70b": "Llama3.1-70B",
    "llama3.1-405b": "Llama3.1-405B",
}


class TreeVisualizationGenerator:
    """Generates visualizations for tree growth metrics"""

    def __init__(self, output_dir: Path):
        """Initialize generator with output directory"""
        self.output_dir = output_dir
        self.tree_metrics_dir = output_dir / "tree_metrics"
        self.tree_metrics_dir.mkdir(exist_ok=True, parents=True)

    def generate_visualizations(self, metrics: dict):
        """Generate all tree growth visualizations"""
        self._visualize_tree_growth(metrics)
        self._visualize_path_analysis(metrics)
        self._visualize_concept_depth_distribution(metrics)
        self._visualize_concept_depth_distribution_filtered(metrics)
        self._visualize_difficulty_distribution(metrics)
        self._visualize_combined_heatmaps(metrics)

    def _visualize_tree_growth(self, metrics: dict):
        """Generate tree growth visualizations"""
        plt.rcParams.update(
            {
                "font.family": "serif",
                "text.usetex": False,
                "axes.linewidth": 1.2,
                "axes.edgecolor": "#333333",
                "grid.alpha": 0.3,
                "font.size": 12,
                "axes.labelsize": 14,
                "axes.titlesize": 16,
            }
        )

        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        fig.set_dpi(300)

        # Color scheme
        main_color = "#2f5d8a"

        # Plot 1: Node Expansion
        depths = list(metrics["tree_growth_patterns"].keys())
        nodes = list(metrics["tree_growth_patterns"].values())

        ax1.plot(
            depths,
            nodes,
            marker="o",
            color=main_color,
            linewidth=2.5,
            markersize=8,
            markeredgecolor="white",
            markeredgewidth=1.5,
        )
        ax1.set_title("Node Expansion Pattern Over Time", pad=20)
        ax1.set_xlabel("Tree Depth")
        ax1.set_ylabel("Number of Nodes")
        ax1.grid(True, alpha=0.3, linestyle="--")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        # Plot 2: Cumulative Growth
        cumulative_nodes = np.cumsum(nodes)
        ax2.plot(
            depths,
            cumulative_nodes,
            marker="o",
            color=main_color,
            linewidth=2.5,
            markersize=8,
            markeredgecolor="white",
            markeredgewidth=1.5,
        )
        ax2.set_title("Cumulative Tree Growth", pad=20)
        ax2.set_xlabel("Tree Depth")
        ax2.set_ylabel("Total Nodes")
        ax2.grid(True, alpha=0.3, linestyle="--")
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)

        # Layout and spacing
        plt.tight_layout(h_pad=3.0)

        # Save with high quality
        plt.savefig(
            self.tree_metrics_dir / "tree_growth.png",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
        plt.close()

    def _visualize_path_analysis(self, metrics: dict):
        """Generate path analysis visualizations"""
        plt.rcParams.update(
            {
                "font.family": "serif",
                "font.size": 12,
                "axes.labelsize": 14,
                "axes.titlesize": 16,
                "axes.linewidth": 1.2,
                "axes.edgecolor": "#333333",
                "grid.alpha": 0.3,
            }
        )

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        fig.set_dpi(300)

        # Overall path success rates
        main_color = "#2f5d8a"
        sns.lineplot(
            x=list(metrics["path_success_rates"].keys()),
            y=list(metrics["path_success_rates"].values()),
            marker="o",
            linewidth=2.5,
            markersize=8,
            color=main_color,
            markeredgecolor="white",
            markeredgewidth=1.5,
            ax=ax1,
        )
        ax1.set_title("Path Success Rates by Length", pad=20)
        ax1.set_xlabel("Path Length")
        ax1.set_ylabel("Success Rate")
        ax1.grid(True, alpha=0.3, linestyle="--")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        # Path success by concept
        path_concept_df = pd.DataFrame(metrics["path_success_by_concept"])
        sns.heatmap(
            path_concept_df,
            annot=True,
            cmap="YlOrRd",
            fmt=".2f",
            ax=ax2,
            cbar_kws={"label": "Success Rate"},
        )
        ax2.set_title("Path Success Rates by Concept and Length", pad=20)
        ax2.set_xlabel("Path Length")
        ax2.set_ylabel("Concept")

        # Layout and spacing
        plt.tight_layout(h_pad=3.0)

        # Save with high quality
        plt.savefig(
            self.tree_metrics_dir / "path_analysis.png",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
        plt.close()

    def _visualize_concept_depth_distribution(self, metrics: dict):
        """Generate concept depth distribution visualization"""
        plt.figure(figsize=(12, 8))
        depth_dist_df = (
            pd.DataFrame(metrics["concept_depth_distribution"]).fillna(0).astype(int)
        )
        sns.heatmap(depth_dist_df, annot=True, cmap="YlOrRd", fmt="d")
        plt.title("Concept Distribution Across Tree Depth")
        plt.xlabel("Concepts")
        plt.ylabel("Tree Depth")
        plt.tight_layout()
        plt.savefig(self.tree_metrics_dir / "concept_depth_distribution.png")
        plt.close()

    def _visualize_concept_depth_distribution_filtered(self, metrics: dict):
        """Generate filtered concept depth distribution visualization"""
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

        # Filter out depths 0 and 1
        filtered_data = {
            concept: {depth: count for depth, count in depths.items() if int(depth) > 1}
            for concept, depths in metrics["concept_depth_distribution"].items()
        }

        # Create DataFrame and rename columns
        depth_dist_df = pd.DataFrame(filtered_data).fillna(0).astype(int)
        depth_dist_df.rename(columns=concept_names, inplace=True)

        # Plot heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(depth_dist_df, annot=True, cmap="YlOrRd", fmt="d", cbar=False)
        plt.title("Concept Distribution Across Tree Depth")
        plt.xlabel("Concepts")
        plt.ylabel("Tree Depth")
        plt.tight_layout()
        plt.savefig(self.tree_metrics_dir / "filtered_concept_depth_distribution.pdf")
        plt.close()

    def _visualize_difficulty_distribution(self, metrics: dict):
        """Generate difficulty distribution visualization"""
        difficulty_names = {
            "very easy": "Very Easy",
            "easy": "Easy",
            "medium": "Medium",
            "hard": "Hard",
            "very hard": "Very Hard",
        }

        # Filter out depths 0 and 1
        filtered_data = {
            depth: {difficulty: count for difficulty, count in difficulties.items()}
            for depth, difficulties in metrics["nodes_by_difficulty"].items()
            if int(depth) > 1
        }

        # Create DataFrame and rename columns
        difficulty_dist_df = pd.DataFrame(filtered_data).fillna(0).astype(int)
        difficulty_dist_df.rename(columns=difficulty_names, inplace=True)

        # Plot heatmap
        plt.figure(figsize=(6, 8))
        sns.heatmap(
            difficulty_dist_df.T, annot=True, cmap="YlOrRd", fmt="d", cbar=False
        )
        plt.title("Difficulty Distribution Across Tree Depth")
        plt.xlabel("Difficulties")
        plt.ylabel("Tree Depth")
        plt.tight_layout()
        plt.savefig(self.tree_metrics_dir / "difficulty_distribution.pdf")
        plt.close()

    def _visualize_combined_heatmaps(self, metrics: dict):
        """Generate combined heatmaps for difficulty and concept depth distribution"""
        # Define ordered difficulty names with proper display names
        difficulties_order = ["very easy", "easy", "medium", "hard", "very hard"]
        difficulty_names = {
            "very easy": "Very Easy",
            "easy": "Easy",
            "medium": "Medium",
            "hard": "Hard",
            "very hard": "Very Hard",
        }
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

        # Filter out depths 0 and 1 for difficulties
        filtered_difficulty_data = {
            depth: {difficulty: count for difficulty, count in difficulties.items()}
            for depth, difficulties in metrics["nodes_by_difficulty"].items()
            if int(depth) > 1
        }

        # Filter out depths 0 and 1 for concepts
        filtered_concept_data = {
            concept: {depth: count for depth, count in depths.items() if int(depth) > 1}
            for concept, depths in metrics["concept_depth_distribution"].items()
        }

        # Create DataFrames and rename columns/indices
        difficulty_dist_df = (
            pd.DataFrame(filtered_difficulty_data).fillna(0).astype(int)
        )
        # Reorder rows according to difficulty order and rename
        difficulty_dist_df = difficulty_dist_df.reindex(difficulties_order).rename(
            index=difficulty_names
        )

        concept_dist_df = pd.DataFrame(filtered_concept_data).fillna(0).astype(int)
        concept_dist_df.rename(columns=concept_names, inplace=True)

        # Plot combined heatmaps side by side
        fig, (ax1, ax2) = plt.subplots(
            1, 2, figsize=(24, 5), gridspec_kw={"width_ratios": [1, 2]}
        )

        sns.heatmap(
            difficulty_dist_df.T,
            annot=True,
            cmap="YlOrRd",
            fmt="d",
            ax=ax1,
            annot_kws={"size": 20, "weight": "bold"},
            cbar=False,
        )
        ax1.set_title(
            "Difficulty Distribution Across Tree Depth", fontsize=16, weight="bold"
        )
        ax1.set_ylabel("Tree Depth", fontsize=14, weight="bold")
        ax1.tick_params(axis="x", labelsize=14)
        plt.setp(ax1.get_xticklabels(), weight="bold")

        sns.heatmap(
            concept_dist_df,
            annot=True,
            cmap="YlOrRd",
            fmt="d",
            ax=ax2,
            annot_kws={"size": 18, "weight": "bold"},
            cbar=False,
        )
        ax2.set_title(
            "Concept Distribution Across Tree Depth", fontsize=16, weight="bold"
        )
        ax2.set_ylabel("Tree Depth", fontsize=14, weight="bold")
        ax2.tick_params(axis="x", labelsize=14)
        plt.setp(ax2.get_xticklabels(), weight="bold")

        plt.tight_layout()
        plt.savefig(self.tree_metrics_dir / "combined_heatmaps.pdf")
        plt.close()


if __name__ == "__main__":
    for model in ["4o", "4o-mini", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]:
        tree_visualizer = TreeVisualizationGenerator(
            Path(f"experiments/{model}/average_metrics/whole_tree")
        )
        metrics = json.load(
            open(f"experiments/{model}/average_metrics/whole_tree/tree_metrics.json")
        )
        tree_visualizer.generate_visualizations(metrics)
