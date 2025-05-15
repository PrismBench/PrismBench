import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Keep the same model configuration style
models = {
    "4o": {
        "display": "GPT4o",
        "color": "#1f77b4",  # Distinct blue
    },
    "4o-mini": {
        "display": "GPT4o-Mini",
        "color": "#ff7f0e",  # Distinct orange
    },
    "llama3.1-405b": {
        "display": "Llama3.1-405B",
        "color": "#9467bd",  # Distinct purple
    },
}

# Define difficulty colors
difficulty_colors = {
    "very easy": "#c8e6c9",  # Light green
    "easy": "#fff9c4",  # Light yellow
    "medium": "#ffcc80",  # Light orange
    "hard": "#ffab91",  # Light red
    "very hard": "#ef9a9a",  # Darker red
}

# Add concept display mapping at the top with other configurations
concept_display_names = {
    "loops": "Loops",
    "dynamic_programming": "Dyn. Prog.",
    "recursion": "Recursion",
    "algorithms": "Algorithms",
    "data_structures": "Data Struct.",
    "conditional": "Conditionals",
    "conditionals": "Conditionals",
    "error_handling": "Error Hand.",
}

# Add pattern display mapping at the top with other configurations
pattern_display_names = {
    "breadth_first_search": "BFS",
    "define": "Define",
    "set": "Set",
    "list": "List",
    "dictionary": "Dict",
    "dynamic_programming": "DP",
    "recursive_backtracking": "Rec. Back.",
    "greedy_algorithm": "Greedy",
    "binary_search": "Bin. Search",
    "depth_first_search": "DFS",
    "sorting": "Sort",
    "merge_sort": "Merge Sort",
    "quick_sort": "Quick Sort",
    "bubble_sort": "Bubble Sort",
    "insertion_sort": "Insert Sort",
    "deque": "Deque",
    "breadth-first search (BFS)": "BFS",
    "backtracking": "Backtr.",
    "iterative DP table filling": "Iter. DP Fill",
    "iterative dynamic programming": "Iter. DP",
    "dynamic programming": "Dyn. Prog.",
    "greedy algorithm": "Greedy",
    "breadth-first search": "BFS",
    "conditional checks": "Cond. Check",
    "dynamic programming with binary search": "DP BS",
    "binary search for efficient lookup": "BS",
    "bottom-up approach": "Bottom Up",
    "prefix sum with hashmap": "Sum Hash",
    "memoization": "Memo.",
    "binary search": "Bin. Search",
    "iterative approach": "Iter. App.",
    "early termination": "Early Term.",
    "sliding window": "Sliding Win.",
    "depth-first search (DFS)": "DFS",
    "priority queue (min-heap)": "Priority Q.",
    "precomputation of palindromes": "Pal. Lengths",
}


def analyze_concept_performance(data, model_name):
    """
    Analyze concept and pattern performance for a given model.
    Returns the 4 worst concepts and their 3 worst patterns each.
    """
    model_data = data["concept_pattern_correlations"].get(model_name, {})
    concept_metrics = []

    # Calculate combined metric for each concept
    for concept, concept_data in model_data.items():
        patterns = concept_data.get("pattern_insights", [])
        if not patterns:
            continue

        # Calculate combined score: average success ratio * total pattern count
        total_patterns = sum(p["usage_count"] for p in patterns)
        avg_success = sum(p["success_ratio"] for p in patterns) / len(patterns)
        combined_score = avg_success * total_patterns

        worst_patterns = sorted(patterns, key=lambda x: x["success_ratio"])[:5]

        concept_metrics.append(
            {
                "concept": concept,
                "combined_score": combined_score,
                "avg_success_ratio": avg_success,
                "total_patterns": total_patterns,
                "worst_patterns": [
                    {
                        "pattern": p["pattern"],
                        "success_ratio": p["success_ratio"],
                        "usage_count": p["usage_count"],
                        "by_difficulty": p["by_difficulty"],
                    }
                    for p in worst_patterns
                ],
            }
        )

    # Sort concepts by combined score (lower is worse)
    concept_metrics.sort(key=lambda x: x["combined_score"])
    return concept_metrics[:4]


def create_pattern_performance_visualization(experiment_dir: Path, output_dir: Path):
    """Generate publication-quality visualization of pattern performance across models."""

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

    # Create figure with three subplots horizontally (one per model)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 18), dpi=300)
    fig.subplots_adjust(hspace=1.5)  # Increase the padding between subfigures
    axes = {"4o": ax1, "4o-mini": ax2, "llama3.1-405b": ax3}

    # Load data
    with open(experiment_dir / "analysis_results" / "comparative_analysis.json") as f:
        data = json.load(f)

    # Plot for each model
    for model_name, ax in axes.items():
        worst_concepts = analyze_concept_performance(data, model_name)

        # Adjust spacing and widths
        n_patterns_per_concept = 5
        bar_width = 0.9  # Reduced from 0.8 to make bars thinner
        pattern_spacing = 0.8  # Add spacing between pattern bars
        concept_spacing = 2.0  # Keep the same concept group spacing
        group_width = n_patterns_per_concept * (bar_width + pattern_spacing)

        pattern_positions = []
        pattern_labels = []

        for concept_idx, concept_data in enumerate(worst_concepts):
            concept_start = concept_idx * (group_width + concept_spacing)

            for pattern_idx, pattern in enumerate(concept_data["worst_patterns"]):
                x_pos = concept_start + (
                    pattern_idx * (bar_width + pattern_spacing)
                )  # Add pattern_spacing to position calculation
                pattern_positions.append(x_pos)
                pattern_labels.append(
                    pattern_display_names.get(pattern["pattern"], pattern["pattern"])
                )
                bottom = 0

                # Stack difficulties with success ratios instead of usage counts
                for difficulty in ["very easy", "easy", "medium", "hard", "very hard"]:
                    difficulty_data = pattern["by_difficulty"].get(difficulty, {})
                    success_ratio = difficulty_data.get("success_ratio", 0)
                    usage_count = difficulty_data.get("usage_count", 0)

                    if usage_count > 0:  # Only plot if there are samples
                        bar = ax.bar(
                            x_pos,
                            success_ratio,  # Plot success ratio instead of usage
                            bottom=bottom,
                            width=bar_width,
                            color=difficulty_colors[difficulty],
                            edgecolor="black",
                            linewidth=0.9,
                            alpha=0.7,
                            zorder=2,
                        )

                        bottom += success_ratio

                # Remove the success ratio label from top since it's now the y-axis

        # Set up x-axis ticks and labels for patterns
        ax.set_xticks(pattern_positions)
        ax.set_xticklabels(
            pattern_labels,
            rotation=50,
            ha="right",
            va="top",
            fontsize=18,
            fontweight="bold",
        )
        ax.tick_params(axis="x", pad=5)

        # Set up secondary x-axis for concept labels
        ax2 = ax.twiny()
        concept_positions = [
            idx * (group_width + concept_spacing) + (group_width / 2) - (bar_width / 2)
            for idx in range(len(worst_concepts))
        ]
        ax2.set_xticks(
            concept_positions,
        )

        # Use the mapping for concept display names
        concept_labels = [
            concept_display_names.get(concept["concept"], concept["concept"])
            for concept in worst_concepts
        ]

        ax2.set_xticklabels(
            concept_labels,
            fontsize=24,
            fontweight="bold",
            rotation=0,
            ha="center",
            va="bottom",
        )

        # Update tick parameters
        ax2.tick_params(axis="x", pad=5, labelsize=18)

        # Add extra padding to x-axis limits
        xlim = ax.get_xlim()
        padding = 1.0  # Increased from 1.0
        ax.set_xlim(xlim[0] - padding, xlim[1] + padding)
        ax2.set_xlim(ax.get_xlim())

        # Move concept axis much further down
        ax2.spines["top"].set_visible(False)
        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        ax2.spines["bottom"].set_position(("outward", 120))
        ax2.tick_params(axis="x", pad=10)

        # Customize subplot
        ax.set_title(
            f"{models[model_name]['display']}",
            pad=20,
            fontsize=22,
            fontweight="bold",
        )
        ax.set_xlabel("")  # Remove xlabel since we have two sets of labels
        ax.set_ylabel("Success Ratio by Difficulty", fontsize=20, fontweight="bold")
        # Add grid and remove top/right spines
        ax.grid(True, linestyle="--", alpha=0.3, zorder=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Adjust y-axis tick parameters and font size
        ax.tick_params(
            axis="y", labelsize=25, width=1.2
        )  # Increased y-axis tick label size
        # Adjust y-limit (no need for extra space at bottom now)
        ax.set_ylim(bottom=0, top=1)  # Success ratios go from 0 to 1

    # Add unified legend at the bottom center
    handles = [
        plt.Rectangle((0, 0), 1, 1, fc=color, alpha=0.7)
        for color in difficulty_colors.values()
    ]
    labels = [level.title() for level in difficulty_colors.keys()]
    # fig.legend(
    #     handles,
    #     labels,
    #     loc="center",
    #     bbox_to_anchor=(0.5, -0.1),
    #     title="Difficulty Levels",
    #     frameon=True,
    #     fancybox=True,
    #     shadow=True,
    #     ncol=5,
    # )

    plt.tight_layout()


    # Save outputs with adjusted bbox_inches to include legend
    output_dir.mkdir(exist_ok=True, parents=True)
    for fmt in ["pdf", "png"]:
        plt.savefig(
            output_dir / f"pattern_performance_analysis.{fmt}",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
            pad_inches=0.3,
        )
    plt.close()


if __name__ == "__main__":
    experiment_dir = Path("/Users/ahvra/Nexus/Prism")
    output_dir = experiment_dir / "experiments" / "comparative_analysis"
    create_pattern_performance_visualization(experiment_dir, output_dir)
