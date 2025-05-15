import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

models = {
    "4o": {
        "display": "GPT4o",
        "color": "#1f77b4",
        "linestyle": "-",
        "auc_alpha": 0.15,
    },  # Distinct blue
    "4o-mini": {
        "display": "GPT4o-Mini",
        "color": "#ff7f0e",
        "linestyle": "--",
        "auc_alpha": 0.2,
    },  # Distinct orange
    "llama3.1-8b": {
        "display": "Llama3.1-8B",
        "color": "#2ca02c",
        "linestyle": "-.",
        "auc_alpha": 0.25,
    },  # Distinct green
    "llama3.1-70b": {
        "display": "Llama3.1-70B",
        "color": "#d62728",
        "linestyle": ":",
        "auc_alpha": 0.3,
    },  # Distinct red
    "llama3.1-405b": {
        "display": "Llama3.1-405B",
        "color": "#9467bd",
        "linestyle": "-",
        "auc_alpha": 0.35,
    },  # Distinct purple
}


def compare_error_distributions(experiment_dir: Path, output_dir: Path):
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
    all_data = []

    for model_name, config in models.items():
        metrics_path = (
            experiment_dir
            / model_name
            / "average_metrics"
            / "phase_3"
            / "error_metrics.json"
        )
        try:
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
            data = pd.DataFrame(metrics["error_distributions"]).transpose()
            data["model"] = config["display"]
            all_data.append(data)
        except FileNotFoundError:
            print(f"Warning: Missing error metrics for {model_name}")

    combined_data = pd.concat(all_data, ignore_index=True)
    combined_data_filled = combined_data.fillna(0)

    # Get column categories
    root_cause_columns = [
        col
        for col in combined_data_filled.columns
        if col.startswith("root_") and col != "root_order_error"
    ]
    root_cause_columns.append("model")

    # Group by 'model' and compute the sum of root causes for each model
    root_cause_frequencies = (
        combined_data_filled[root_cause_columns].groupby("model").sum()
    )

    # Calculate total tests conducted per model
    root_cause_frequencies["total_tests"] = root_cause_frequencies.sum(axis=1)

    # Normalize the root cause frequencies by total tests
    normalized_frequencies = root_cause_frequencies.div(
        root_cause_frequencies["total_tests"], axis=0
    ).drop(columns=["total_tests"])

    # Refine the color palette and add gridlines for better clarity
    color_palette = sns.color_palette("tab10", n_colors=normalized_frequencies.shape[1])

    # Plot the refined stacked bar chart
    normalized_frequencies.plot(
        kind="bar",
        stacked=True,
        figsize=(14, 7),
        alpha=0.9,
        width=0.8,
        color=color_palette,
    )

    # Add gridlines for better readability
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Improve title and axis labels
    plt.title(
        "Comparison of Root Cause Frequencies Across Models",
        fontsize=16,
    )
    plt.xlabel("Models", fontsize=12)
    plt.ylabel("Normalized Root Cause Frequencies", fontsize=12)

    # Move legend to a less cluttered position
    plt.legend(title="Root Causes", bbox_to_anchor=(1.05, 1), loc="upper left")

    # Ensure proper tick rotation and spacing
    plt.xticks(rotation=45, fontsize=10)
    plt.tight_layout()

    # Save outputs
    output_path = Path("/Users/ahvra/Nexus/Prism/experiments/comparative_analysis")
    output_path.mkdir(exist_ok=True, parents=True)
    for fmt in ["pdf", "png"]:
        plt.savefig(
            output_path / f"root_cause_comparison_stacked_chart.{fmt}",
            bbox_inches="tight",
            dpi=300,
        )

    # Show refined visualization
    plt.show()


if __name__ == "__main__":
    experiment_dir = Path("/Users/ahvra/Nexus/Prism/experiments")
    compare_error_distributions(experiment_dir, experiment_dir)
