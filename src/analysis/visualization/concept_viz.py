from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class ConceptVisualizationGenerator:
    """Generates visualizations for concept mastery metrics"""

    def __init__(self, output_dir: Path):
        """Initialize generator with output directory"""
        self.output_dir = output_dir
        self.concept_metrics_dir = output_dir / "concept_metrics"
        self.concept_metrics_dir.mkdir(exist_ok=True, parents=True)

    def generate_visualizations(self, metrics: dict):
        """Generate all concept mastery visualizations"""
        self._visualize_mastery_progression(metrics)
        self._visualize_difficulty_scaling(metrics)
        self._visualize_concept_combinations(metrics)
        self._visualize_correlation_matrix(metrics)
        self._visualize_attempts_distribution(metrics)
        self._visualize_success_heatmaps(metrics)
        self._visualize_success_boxplots(metrics)
        self._visualize_concept_performance_over_time(metrics)
        self._visualize_concept_complexity_impact(metrics)

    def _visualize_mastery_progression(self, metrics: dict):
        """Generate concept mastery progression visualizations"""
        plt.figure(figsize=(15, 8))
        for concept, progression in metrics["concept_mastery_distribution"].items():
            difficulties = [p["difficulty"] for p in progression]
            success_rates = [p["success_rate"] for p in progression]
            plt.plot(
                difficulties, success_rates, marker="o", label=concept, linewidth=2
            )

        plt.title("Concept Mastery Progression Across Difficulties", fontsize=16)
        plt.xlabel("Difficulty Level", fontsize=14)
        plt.ylabel("Success Rate", fontsize=14)
        plt.legend(title="Concept", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(
            self.concept_metrics_dir / "concept_success_rate_per_difficulty.png"
        )
        plt.close()

    def _visualize_difficulty_scaling(self, metrics: dict):
        """Generate difficulty scaling visualizations"""
        plt.figure(figsize=(15, 12))
        concepts = list(metrics["difficulty_scaling_patterns"].keys())
        difficulties = ["very easy", "easy", "medium", "hard", "very hard"]

        # Create heatmap data for adjusted_success
        heatmap_data = np.zeros((len(concepts), len(difficulties)))
        for i, concept in enumerate(concepts):
            for j, diff in enumerate(difficulties):
                for pattern in metrics["difficulty_scaling_patterns"][concept]:
                    if pattern["difficulty"] == diff:
                        heatmap_data[i, j] = pattern["adjusted_success"]
                        break

        # Plot heatmap for Adjusted Success Rates
        plt.subplot(2, 1, 1)
        sns.heatmap(
            heatmap_data,
            xticklabels=difficulties,
            yticklabels=concepts,
            cmap="RdYlGn",
            center=0.5,
            annot=True,
            fmt=".2f",
            linewidths=0.5,
            cbar_kws={"label": "Adjusted Success Rate"},
        )
        plt.title("Concept Performance Across Difficulty Levels", fontsize=16)
        plt.xlabel("Difficulty Level", fontsize=14)
        plt.ylabel("Concepts", fontsize=14)

        # Create heatmap data for visit_ratio
        visit_data = np.zeros((len(concepts), len(difficulties)))
        for i, concept in enumerate(concepts):
            for j, diff in enumerate(difficulties):
                for pattern in metrics["difficulty_scaling_patterns"][concept]:
                    if pattern["difficulty"] == diff:
                        visit_data[i, j] = pattern["visit_ratio"]
                        break

        # Plot heatmap for Visit Ratios
        plt.subplot(2, 1, 2)
        sns.heatmap(
            visit_data,
            xticklabels=difficulties,
            yticklabels=concepts,
            cmap="RdYlGn",
            annot=True,
            fmt=".2f",
            linewidths=0.5,
            cbar_kws={"label": "Visit Ratio"},
        )
        plt.title("Visit Ratios Across Difficulty Levels", fontsize=16)
        plt.xlabel("Difficulty Level", fontsize=14)
        plt.ylabel("Concepts", fontsize=14)

        plt.tight_layout()
        plt.savefig(self.concept_metrics_dir / "concept_success_rate_heatmap.png")
        plt.close()

    def _visualize_concept_combinations(self, metrics: dict):
        """Generate concept combinations visualizations"""
        plt.figure(figsize=(15, 15))
        # Create subplots for success rates and visits
        plt.subplot(2, 1, 1)

        # Get unique concepts from tuple keys directly
        unique_concepts = sorted(
            list(
                set(
                    concept
                    for combo in metrics["concept_combinations"].keys()
                    for concept in combo  # Tuple is already iterable
                )
            )
        )
        num_concepts = len(unique_concepts)
        combination_matrix = np.zeros((num_concepts, num_concepts))
        visit_matrix = np.zeros((num_concepts, num_concepts))

        # Fill the matrices with success rates and visits
        for combo, data in metrics["concept_combinations"].items():
            combos_with_these_concepts = [
                c
                for c in metrics["concept_combinations"].keys()
                if combo[0] in c and combo[1] in c
            ]
            if len(combos_with_these_concepts) != 0:
                success_rate = sum(
                    [
                        metrics["concept_combinations"][c]["success_rate"]
                        for c in combos_with_these_concepts
                    ]
                ) / len(combos_with_these_concepts)
                visit_count = sum(
                    [
                        metrics["concept_combinations"][c]["visits"]
                        for c in combos_with_these_concepts
                    ]
                )
            else:
                success_rate = 0
                visit_count = 0

            if len(combo) == 2:  # Focus on pairs for the heatmap
                try:
                    i = unique_concepts.index(combo[0])
                    j = unique_concepts.index(combo[1])
                    combination_matrix[i][j] = success_rate
                    combination_matrix[j][i] = success_rate
                    visit_matrix[i][j] = visit_count
                    visit_matrix[j][i] = visit_count
                except ValueError:
                    continue

        # Plot success rate heatmap
        sns.heatmap(
            combination_matrix,
            xticklabels=unique_concepts,
            yticklabels=unique_concepts,
            cmap="RdYlGn",
            center=0.5,
            annot=True,
            fmt=".2f",
            linewidths=0.5,
            cbar_kws={"label": "Success Rate"},
        )
        plt.title("Concept Combination Success Rates", fontsize=16)

        # Plot visit count heatmap
        plt.subplot(2, 1, 2)
        sns.heatmap(
            visit_matrix,
            xticklabels=unique_concepts,
            yticklabels=unique_concepts,
            cmap="YlOrRd",
            annot=True,
            fmt="g",
            linewidths=0.5,
            cbar_kws={"label": "Visit Count"},
        )
        plt.title("Concept Combination Visit Counts", fontsize=16)

        plt.tight_layout()
        plt.savefig(self.concept_metrics_dir / "concept_pair_success_rate_heatmap.png")
        plt.close()

    def _visualize_correlation_matrix(self, metrics: dict):
        """Generate correlation matrix visualization"""
        # Calculate correlation between concepts based on success rates
        success_rate_df = pd.DataFrame(
            [
                {
                    "Concept 1": concept.split("+")[0].strip(),
                    "Concept 2": concept.split("+")[1].strip(),
                    "Success Rate": (
                        data["success_rate"] if "success_rate" in data else np.nan
                    ),
                }
                for concept, data in metrics["concept_combinations"].items()
                if "+" in concept
            ]
        ).dropna()

        # Add debug print to check the dataframe
        if success_rate_df.empty:
            print("Warning: No valid concept combinations found for correlation matrix")
            return

        # Pivot the data to create a matrix
        pivot_df = success_rate_df.pivot_table(
            index="Concept 1", columns="Concept 2", values="Success Rate"
        )
        correlation_matrix = pivot_df.corr()

        plt.figure(figsize=(12, 10))
        sns.heatmap(
            correlation_matrix,
            annot=True,
            cmap="coolwarm",
            fmt=".2f",
            linewidths=0.5,
        )
        plt.title("Correlation Matrix of Concept Success Rates", fontsize=16)
        plt.tight_layout()
        plt.savefig(self.concept_metrics_dir / "concept_correlation_matrix.png")
        plt.close()

    def _visualize_attempts_distribution(self, metrics: dict):
        """Generate attempts distribution visualization"""
        attempts_data = []
        for combo, data in metrics["concept_combinations"].items():
            # Convert tuple to string representation
            combination = " + ".join(combo) if isinstance(combo, tuple) else str(combo)
            attempts = data.get("total_attempts", 0)
            attempts_data.append({"Combination": combination, "Attempts": attempts})

        if attempts_data:
            attempts_df = pd.DataFrame(attempts_data)
            plt.figure(figsize=(20, 12))
            sns.barplot(data=attempts_df, x="Combination", y="Attempts", palette="Set3")
            plt.title("Total Attempts by Concept Combinations", fontsize=16)
            plt.xlabel("Concept Combination", fontsize=14)
            plt.ylabel("Number of Attempts", fontsize=14)
            plt.xticks(rotation=90, ha="right")
            plt.tight_layout()
            plt.savefig(self.concept_metrics_dir / "concept_attempt_barchart.png")
            plt.close()

    def _visualize_success_heatmaps(self, metrics: dict):
        """Generate success rate heatmaps"""
        # Create success rate by difficulty heatmap
        success_over_time_df = pd.DataFrame(
            [
                {
                    "Concept": concept,
                    "Difficulty": p["difficulty"],
                    "Success Rate": p["success_rate"],
                    "Visits": p["visits"],
                }
                for concept, progressions in metrics[
                    "concept_mastery_distribution"
                ].items()
                for p in progressions
            ]
        )

        # Pivot the data to have difficulties as columns
        pivot_success = success_over_time_df.pivot_table(
            index="Concept",
            columns="Difficulty",
            values="Success Rate",
            aggfunc="mean",
        )

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            pivot_success,
            annot=True,
            cmap="RdYlGn",
            fmt=".2f",
            linewidths=0.5,
        )
        plt.title("Average Success Rate by Concept and Difficulty", fontsize=16)
        plt.xlabel("Difficulty Level", fontsize=14)
        plt.ylabel("Concept", fontsize=14)
        plt.tight_layout()
        plt.savefig(
            self.concept_metrics_dir / "concept_difficulty_success_rate_heatmap.png"
        )
        plt.close()

        # Create visit count heatmap
        visit_ratio_pivot = success_over_time_df.pivot_table(
            index="Concept", columns="Difficulty", values="Visits", aggfunc="sum"
        )

        plt.figure(figsize=(12, 10))
        sns.heatmap(
            visit_ratio_pivot,
            cmap="YlGnBu",
            annot=True,
            fmt="g",
        )
        plt.title("Total Visits by Concept and Difficulty", fontsize=16)
        plt.xlabel("Difficulty Level", fontsize=14)
        plt.ylabel("Concept", fontsize=14)
        plt.tight_layout()
        plt.savefig(self.concept_metrics_dir / "concept_difficulty_visit_heatmap.png")
        plt.close()

    def _visualize_success_boxplots(self, metrics: dict):
        """Generate success rate box plots"""
        # Create box plots for success rates by difficulty
        success_over_time_df = pd.DataFrame(
            [
                {
                    "Concept": concept,
                    "Difficulty": p["difficulty"],
                    "Success Rate": p["success_rate"],
                }
                for concept, progressions in metrics[
                    "concept_mastery_distribution"
                ].items()
                for p in progressions
            ]
        )

        plt.figure(figsize=(12, 6))
        sns.boxplot(
            data=success_over_time_df,
            x="Difficulty",
            y="Success Rate",
            palette="Set3",
        )
        plt.title("Success Rate Distribution by Difficulty", fontsize=16)
        plt.xlabel("Difficulty Level", fontsize=14)
        plt.ylabel("Success Rate", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.concept_metrics_dir / "success_rate_boxplot_difficulty.png")
        plt.close()

        # Create box plots for success rates by concept
        plt.figure(figsize=(15, 6))
        sns.boxplot(
            data=success_over_time_df,
            x="Concept",
            y="Success Rate",
            palette="Set3",
        )
        plt.title("Success Rate Distribution by Concept", fontsize=16)
        plt.xlabel("Concept", fontsize=14)
        plt.ylabel("Success Rate", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.concept_metrics_dir / "success_rate_boxplot_concept.png")
        plt.close()

    def _visualize_concept_performance_over_time(self, metrics: dict):
        """Generate concept performance over time visualizations"""
        # Create line plots for each concept's performance progression
        plt.figure(figsize=(15, 8))
        for concept, progression in metrics["concept_mastery_distribution"].items():
            difficulties = [p["difficulty"] for p in progression]
            success_rates = [p["success_rate"] for p in progression]
            visits = [p["visits"] for p in progression]

            # Size points by number of visits
            sizes = [50 * (v / max(visits)) for v in visits]

            plt.scatter(
                difficulties,
                success_rates,
                s=sizes,
                alpha=0.6,
                label=concept,
            )
            plt.plot(difficulties, success_rates, linestyle="--", alpha=0.4)

        plt.title("Concept Performance Progression", fontsize=16)
        plt.xlabel("Difficulty Level", fontsize=14)
        plt.ylabel("Success Rate", fontsize=14)
        plt.grid(True, linestyle=":", alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(self.concept_metrics_dir / "concept_performance_progression.png")
        plt.close()

    def _visualize_concept_complexity_impact(self, metrics: dict):
        """Generate visualizations for concept complexity impact"""
        # Extract and prepare data
        complexity_data = []
        for concept, patterns in metrics["performance_degradation"].items():
            for pattern in patterns:
                complexity_data.append(
                    {
                        "Concept": concept,
                        "Complexity": pattern["complexity"],
                        "Relative Performance": pattern["relative_performance"],
                        "Absolute Success": pattern["absolute_success"],
                        "Sample Size": pattern["sample_size"],
                    }
                )

        if complexity_data:
            df = pd.DataFrame(complexity_data)

            # Plot relative performance degradation
            plt.figure(figsize=(12, 6))
            sns.lineplot(
                data=df,
                x="Complexity",
                y="Relative Performance",
                hue="Concept",
                marker="o",
            )
            plt.title("Performance Degradation with Increasing Complexity", fontsize=16)
            plt.xlabel("Number of Concepts", fontsize=14)
            plt.ylabel("Relative Performance", fontsize=14)
            plt.grid(True, linestyle=":", alpha=0.3)
            plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
            plt.tight_layout()
            plt.savefig(self.concept_metrics_dir / "concept_complexity_impact.png")
            plt.close()

            # Plot absolute success rates
            plt.figure(figsize=(12, 6))
            sns.lineplot(
                data=df,
                x="Complexity",
                y="Absolute Success",
                hue="Concept",
                marker="o",
            )
            plt.title("Absolute Success Rate vs Complexity", fontsize=16)
            plt.xlabel("Number of Concepts", fontsize=14)
            plt.ylabel("Success Rate", fontsize=14)
            plt.grid(True, linestyle=":", alpha=0.3)
            plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
            plt.tight_layout()
            plt.savefig(self.concept_metrics_dir / "concept_complexity_success.png")
            plt.close()


if __name__ == "__main__":
    for model in ["4o-mini", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]:
        concept_visualizer = ConceptVisualizationGenerator(
            Path(f"experiments/{model}/average-metrics/phase-1")
        )
        metrics = json.load(
            open(f"experiments/{model}/average-metrics/phase-1/concept_metrics.json")
        )
        concept_visualizer.generate_visualizations(metrics)
