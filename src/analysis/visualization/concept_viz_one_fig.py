from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

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
difficulty_names = {
    "very easy": "Very Easy",
    "easy": "Easy",
    "medium": "Medium",
    "hard": "Hard",
    "very hard": "Very Hard",
}


class ConceptVisualizationGenerator:
    """Generates visualizations for concept mastery metrics"""

    def __init__(self, output_dir: Path, model_name: str):
        """Initialize generator with output directory"""
        self.output_dir = output_dir
        self.concept_metrics_dir = output_dir / "concept_metrics"
        self.concept_metrics_dir.mkdir(exist_ok=True, parents=True)
        self.difficulties = ["very easy", "easy", "medium", "hard", "very hard"]
        self.model_names = model_name
        # Add model name mappings
        self.model_display_names = {
            "4o": "GPT-4o",
            "4o-mini": "GPT-4o-mini",
            "llama3.1-8b": "Llama3.1-8B",
            "llama3.1-70b": "Llama3.1-70B",
            "llama3.1-405b": "Llama3.1-405B",
        }

    def generate_visualizations(self, metrics: dict):
        """Generate all concept mastery visualizations"""
        plt.figure(figsize=(20, 7))

        # Get unique concepts from tuple keys for combination matrices
        unique_concepts = sorted(
            list(
                set(
                    concept
                    for combo in metrics["concept_combinations"].keys()
                    for concept in combo.split("+")
                )
            )
        )
        num_concepts = len(unique_concepts)
        combination_matrix = np.zeros((num_concepts, num_concepts))
        visit_matrix = np.zeros((num_concepts, num_concepts))

        # Fill the matrices with success rates and visits
        for combo, data in metrics["concept_combinations"].items():
            if len(combo.split("+")) == 2:  # Focus on pairs for the heatmap
                try:
                    i = unique_concepts.index(combo.split("+")[0])
                    j = unique_concepts.index(combo.split("+")[1])
                    combination_matrix[i][j] = data.get("success_rate", 0)
                    combination_matrix[j][i] = data.get("success_rate", 0)
                    visit_matrix[i][j] = data.get("visits", 0)
                    visit_matrix[j][i] = data.get("visits", 0)
                except ValueError:
                    continue

        # Plot success rate heatmap (left)
        plt.subplot(1, 2, 1)
        sns.heatmap(
            combination_matrix,
            xticklabels=[concept_names[c] for c in unique_concepts],
            yticklabels=[concept_names[c] for c in unique_concepts],
            cmap="RdYlGn",
            center=0.5,
            annot=True,
            fmt=".2f",
            linewidths=0.5,
            cbar=False,
            annot_kws={"size": 14, "weight": "bold"},
        )
        plt.title("Concept Combination Success Rates", fontsize=18, weight="bold")
        plt.xlabel("Concepts", fontsize=16, weight="bold")
        plt.ylabel("Concepts", fontsize=16, weight="bold")
        ax = plt.gca()
        ax.set_xticklabels(
            ax.get_xticklabels(), size=14, weight="bold"
        )  # Make x-axis labels bigger
        ax.set_yticklabels(
            ax.get_yticklabels(), size=14, weight="bold"
        )  # Make y-axis labels bigger
        # Plot visit count heatmap (right)
        plt.subplot(1, 2, 2)
        sns.heatmap(
            visit_matrix,
            xticklabels=[concept_names[c] for c in unique_concepts],
            yticklabels=[concept_names[c] for c in unique_concepts],
            cmap="YlOrRd",
            annot=True,
            fmt=".2f",
            linewidths=0.5,
            cbar=False,
            annot_kws={"size": 14, "weight": "bold"},
        )  # Make numbers bold and bigger

        plt.title("Concept Combination Visit Counts", fontsize=18, weight="bold")
        plt.xlabel("Concepts", fontsize=16, weight="bold")
        
        ax = plt.gca()
        ax.set_xticklabels(
            ax.get_xticklabels(), size=14, weight="bold"
        )  # Make x-axis labels bigger
        ax.set_yticklabels(
            ax.get_yticklabels(), size=14, weight="bold"
        )  # Make y-axis labels bigger
        # Add model name as suptitle with more space at bottom
        display_name = self.model_display_names.get(self.model_names, self.model_names)
        plt.suptitle(display_name, y=-0.05, fontsize=20, weight="bold")

        # Adjust layout with more bottom margin
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)  # Increased bottom margin

        plt.savefig(
            self.concept_metrics_dir
            / f"{self.model_names}_concept_metrics_combined.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.savefig(
            self.concept_metrics_dir
            / f"{self.model_names}_concept_metrics_combined.pdf",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()


if __name__ == "__main__":
    for model in ["4o-mini", "4o", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]:
        concept_visualizer = ConceptVisualizationGenerator(Path(f"experiments"), model)
        metrics = json.load(
            open(f"experiments/{model}/average_metrics/whole_tree/concept_metrics.json")
        )
        concept_visualizer.generate_visualizations(metrics)
