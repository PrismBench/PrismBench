import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

models = {
    "4o": {
        "display": "GPT4o",
        "color": "#1f77b4",
    },  # Distinct blue
    "4o-mini": {
        "display": "GPT4o-Mini",
        "color": "#ff7f0e",
    },  # Distinct orange
    # "llama3.1-8b": {
    #     "display": "Llama3.1-8B",
    #     "color": "#2ca02c",
    # },  # Distinct green
    # "llama3.1-70b": {
    #     "display": "Llama3.1-70B",
    #     "color": "#d62728",
    # },  # Distinct red
    "llama3.1-405b": {
        "display": "Llama3.1-405B",
        "color": "#9467bd",
    },  # Distinct purple
}
# Mapping for concept names
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


def create_nested_radar_chart(ax, model_name, model_data):
    """
    Create a nested radar chart for a single model's performance across different difficulty levels.

    Args:
        ax (matplotlib.axes._subplots.AxesSubplot): The axis to plot on
        model_name (str): Name of the model
        model_data (dict): Dictionary containing model data in the format:
            {
                'concept-difficulty': success_rate
            }
    """
    # Separate data by difficulty levels
    easy_data = {k: v for k, v in model_data.items() if k.endswith("-easy")}
    medium_data = {k: v for k, v in model_data.items() if k.endswith("-medium")}
    hard_data = {k: v for k, v in model_data.items() if k.endswith("-hard")}

    # Get all unique concepts and sort them alphabetically
    concepts = sorted(list(set(k.split("-")[0] for k in model_data.keys())))
    num_concepts = len(concepts)

    # Set up the angles for each concept
    angles = [n / float(num_concepts) * 2 * np.pi for n in range(num_concepts)]
    angles += angles[:1]  # Complete the circle

    # Plot data for each difficulty level with different colors
    difficulty_colors = {"Hard": "#e74c3c", "Medium": "#f1c40f", "Easy": "#2ecc71"}
    for data, label in zip(
        [hard_data, medium_data, easy_data], ["Hard", "Medium", "Easy"]
    ):
        values = [data.get(f"{concept}-{label.lower()}", 0) for concept in concepts]
        values += values[:1]
        ax.plot(
            angles,
            values,
            "o-",
            linewidth=2,
            label=label,
            color=difficulty_colors[label],
        )
        ax.fill(angles, values, alpha=0.25, color=difficulty_colors[label])

    # Set the labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([])  # Remove the angle labels

    labels = [concept_names.get(concept, concept) for concept in concepts]
    for label, angle in zip(labels, angles[:-1]):
        rotation = np.degrees(angle)
        if angle > np.pi / 2 and angle < 3 * np.pi / 2:
            alignment = "right"
        else:
            alignment = "left"
        ax.text(
            angle,
            1.1,  # Move the label further outside the radar chart
            label,
            fontsize=24,
            fontweight="bold",
            ha=alignment,
            va="center",
        )
    # Add gridlines
    ax.set_rlim(0, 1)
    ax.grid(True, alpha=0.5)  # Adjust transparency of grid lines

    # Make the numbers on the grid lines bigger
    ax.tick_params(axis="y", labelsize=15)

    # Add title
    ax.set_title(f"{model_name}", size=26, y=1.1)


def read_concept_mastery_data(experiment_dir: Path):
    """Read concept mastery data from JSON files."""

    difficulty_map = {
        "very easy": "easy",
        "easy": "easy",
        "medium": "medium",
        "hard": "hard",
        "very hard": "hard",
    }

    all_keys = set()
    models_data = {}
    for model_name, config in models.items():
        metrics_path = (
            experiment_dir / model_name / "average_metrics/whole_tree/concept_metrics.json"
        )
        try:
            with open(metrics_path) as f:
                metrics = json.load(f)
                concept_mastery = {}
                for concept, difficulties in metrics[
                    "concept_mastery_distribution"
                ].items():
                    for difficulty, data in difficulties.items():
                        key = f"{concept}-{difficulty_map[difficulty]}"
                        if key not in concept_mastery:
                            concept_mastery[key] = []
                        concept_mastery[key].append(data["success_rate"])
                        all_keys.add(key)
                # Average the success rates for each concept-difficulty key
                for key in concept_mastery:
                    concept_mastery[key] = np.mean(concept_mastery[key])
                models_data[config["display"]] = {
                    "metrics": concept_mastery,
                    "color": config["color"],
                }
        except FileNotFoundError:
            print(f"Warning: Metrics not found for {model_name}")
            continue

    # Ensure all models have the same keys, fill missing keys with zero
    for model_info in models_data.values():
        for key in all_keys:
            if key not in model_info["metrics"]:
                model_info["metrics"][key] = 0.0

    return models_data


def create_concept_mastery_radar_charts(experiment_dir: Path, output_path: Path):
    """Create a single diagram with nested radar charts for concept mastery distribution across models."""
    models_data = read_concept_mastery_data(experiment_dir)

    # Create figure with three subplots
    fig, axes = plt.subplots(
        1, 3, figsize=(30, 8), subplot_kw=dict(projection="polar"), dpi=300
    )
    fig.subplots_adjust(wspace=0.5)

    # Publication-quality styling
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "axes.linewidth": 1.2,
            "axes.edgecolor": "#333333",
            "grid.alpha": 0.5,
            "font.size": 14,
            "axes.labelsize": 16,
            "axes.titlesize": 18,
            "legend.fontsize": 12,
            "legend.frameon": True,
            "legend.framealpha": 0.9,
            "legend.edgecolor": "#333333",
        }
    )

    # Plot each model's radar chart
    for ax, (model_name, model_info) in zip(axes, models_data.items()):
        create_nested_radar_chart(ax, model_name, model_info["metrics"])

    # Add single legend for all plots
    handles, labels = axes[0].get_legend_handles_labels()
    # fig.legend(
    #     handles,
    #     labels,
    #     loc="center right",
    #     bbox_to_anchor=(1.1, 0.5),
    #     borderaxespad=0,
    #     frameon=True,
    #     fancybox=True,
    #     shadow=True,
    # )

    plt.tight_layout()

    # Save outputs
    output_path.mkdir(exist_ok=True, parents=True)
    for fmt in ["pdf", "png"]:
        plt.savefig(
            output_path / f"concept_mastery_radar.{fmt}", bbox_inches="tight", dpi=300
        )
    plt.close()


# Example usage with your data
if __name__ == "__main__":
    experiment_dir = Path("/Users/ahvra/Nexus/Prism/experiments")
    output_dir = experiment_dir / "comparative_analysis"
    output_dir.mkdir(exist_ok=True, parents=True)

    create_concept_mastery_radar_charts(experiment_dir, output_dir)
