import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from collections import defaultdict

models = {
    "4o": {
        "display": "4o",
        "color": "#1f77b4",
        "linestyle": "-",
        "auc_alpha": 0.15,
    },  # Distinct blue
    "4o-mini": {
        "display": "4o-M",
        "color": "#ff7f0e",
        "linestyle": "--",
        "auc_alpha": 0.2,
    },  # Distinct orange
    "llama3.1-8b": {
        "display": "L-8B",
        "color": "#2ca02c",
        "linestyle": "-.",
        "auc_alpha": 0.25,
    },  # Distinct green
    "llama3.1-70b": {
        "display": "L-70B",
        "color": "#d62728",
        "linestyle": ":",
        "auc_alpha": 0.3,
    },  # Distinct red
    "llama3.1-405b": {
        "display": "L-405B",
        "color": "#9467bd",
        "linestyle": "-",
        "auc_alpha": 0.35,
    },  # Distinct purple
}


def compare_tree_growth_phase_one(experiment_dir: Path, output_dir: Path):
    """Generate publication-quality comparative visualization of tree growth patterns."""

    # Create figure with better proportions
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 14), dpi=300)

    # Publication-quality styling without LaTeX
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "axes.linewidth": 1.2,
            "axes.edgecolor": "#333333",
            "grid.alpha": 0.2,
            "font.size": 14,
            "axes.labelsize": 16,
            "axes.titlesize": 18,
            "legend.fontsize": 12,
            "legend.frameon": True,
            "legend.framealpha": 0.9,
            "legend.edgecolor": "#333333",
        }
    )

    for model_name, config in models.items():
        metrics_path = (
            experiment_dir / model_name / "average-metrics/phase-1/tree_metrics.json"
        )

        try:
            with open(metrics_path) as f:
                metrics = json.load(f)

            depths = list(map(int, metrics["tree_growth_patterns"].keys()))
            nodes = list(metrics["tree_growth_patterns"].values())
            cumulative_nodes = np.cumsum(nodes)

            # Enhanced plotting style
            line_style = {
                "marker": "o",
                "label": config["display"],
                "color": config["color"],
                "linewidth": 2.5,
                "markersize": 8,
                "markeredgecolor": "white",
                "markeredgewidth": 1.5,
                "alpha": 0.9,
                "zorder": 3,
            }

            ax1.plot(depths, nodes, **line_style)
            ax2.plot(depths, cumulative_nodes, **line_style)

        except FileNotFoundError:
            print(f"Warning: Metrics not found for {model_name}")
            continue

    # Enhanced subplot styling
    for ax, title in [(ax1, "Node Expansion Pattern"), (ax2, "Cumulative Tree Growth")]:
        ax.set_title(title, pad=20, fontweight="bold")
        ax.set_xlabel("Tree Depth", labelpad=10)
        ax.set_ylabel("Number of Nodes" if ax == ax1 else "Total Nodes", labelpad=10)
        ax.grid(True, linestyle="--", alpha=0.2, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Enhanced legend with better positioning
        legend = ax.legend(
            loc="center left",
            bbox_to_anchor=(1.05, 0.5),
            borderaxespad=0,
            frameon=True,
            fancybox=True,
            shadow=True,
        )
        legend.get_frame().set_facecolor("white")
        legend.get_frame().set_alpha(0.9)

        # Add light background shading for better contrast
        ax.set_facecolor("#F8F9F9")

        # Improve tick labels
        ax.tick_params(axis="both", which="major", labelsize=12)

    # Adjust layout to prevent overlapping
    plt.subplots_adjust(right=0.85, hspace=0.3)

    # Save with publication quality
    output_dir.mkdir(exist_ok=True, parents=True)
    for fmt in ["pdf", "png"]:
        plt.savefig(
            output_dir / f"comparative_tree_growth.{fmt}",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
    plt.close()


def compare_tree_growth_phase_two(experiment_dir: Path, output_dir: Path):
    """Generate publication-quality phase 2 visualization with complexity zones."""

    # Match phase one figure size and DPI
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 14), dpi=300)

    # Match phase one styling exactly
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "axes.linewidth": 1.2,
            "axes.edgecolor": "#333333",
            "grid.alpha": 0.2,
            "font.size": 14,
            "axes.labelsize": 16,
            "axes.titlesize": 18,
            "legend.fontsize": 12,
            "legend.frameon": True,
            "legend.framealpha": 0.9,
            "legend.edgecolor": "#333333",
        }
    )

    # Define complexity zones with more visible colors
    zones = {
        "simple": {
            "range": (2, 4),
            "color": "#ffcdd2",
            "alpha": 0.9,
        },  # Stronger red tint
        "moderate": {
            "range": (4, 7),
            "color": "#fff9c4",
            "alpha": 0.9,
        },  # Stronger yellow
        "complex": {
            "range": (7, 11),
            "color": "#c8e6c9",
            "alpha": 0.9,
        },  # Stronger green
    }

    max_depth = 0
    model_data = {}  # Store data for normalization

    # First pass: collect all data for normalization
    for model_name, config in models.items():
        metrics_path = (
            experiment_dir / model_name / "average-metrics/phase-2/tree_metrics.json"
        )

        try:
            with open(metrics_path) as f:
                metrics = json.load(f)

            growth_patterns = metrics["tree_growth_patterns"]
            depths = sorted(map(int, growth_patterns.keys()))
            max_depth = max(max_depth, max(depths))
            nodes = [growth_patterns[str(d)] for d in depths]
            cumulative_nodes = np.cumsum(nodes)

            model_data[model_name] = {
                "depths": depths,
                "nodes": nodes,
                "cumulative": cumulative_nodes,
            }

        except FileNotFoundError:
            print(f"Warning: Metrics not found for {model_name}")
            continue

    # Second pass: plot normalized data
    for i, (model_name, config) in enumerate(models.items()):
        if model_name not in model_data:
            continue

        data = model_data[model_name]

        # Add small offset to x values to prevent overlap
        offset = (i - len(models) / 2) * 0  # Adjust 0.15 to control separation
        depths_offset = [d + offset for d in data["depths"]]

        # Normalize values to percentages
        nodes_normalized = [n / sum(data["nodes"]) * 100 for n in data["nodes"]]
        # cumulative_normalized = [
        # n / data["cumulative"][-1] * 100 for n in data["cumulative"]
        # ]

        line_style = {
            "marker": "o",
            "label": config["display"],
            "color": config["color"],
            "linewidth": 2.5,
            "markersize": 8,
            "markeredgecolor": "white",
            "markeredgewidth": 1.5,
            "alpha": 0.85,  # Slightly more transparent
            "zorder": 3,
        }

        ax1.plot(depths_offset, [-n for n in nodes_normalized], **line_style)
        # ax2.plot(depths_offset, [-n for n in cumulative_normalized], **line_style)

    # Add complexity zone shading and improved annotations to both plots
    # Add annotations with better positioning
    for ax in [ax1, ax2]:
        ax.invert_yaxis()

    # Configure subplots
    titles = [
        "Node Distribution by Tree Depth\n(% of total nodes at each depth)",
        "Cumulative Distribution\n(% of total nodes up to depth)",
    ]

    # Match phase one subplot styling
    for ax, title in zip([ax1], titles):
        ax.set_title(title, pad=20, fontweight="bold")
        ax.set_xlabel("Tree Depth", labelpad=10)
        ax.set_ylabel("Percentage of Nodes", labelpad=10)
        ax.grid(True, linestyle="--", alpha=0.5, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_facecolor("#F8F9F9")
        ax.tick_params(axis="both", which="major", labelsize=12)

        # Match phase one legend styling
        if ax == ax1:
            handles, labels = ax.get_legend_handles_labels()
            legend = ax.legend(
                handles=handles,
                loc="center left",
                bbox_to_anchor=(1.05, 0.5),
                borderaxespad=0,
                frameon=True,
                fancybox=True,
                shadow=True,
            )
            legend.get_frame().set_facecolor("white")
            legend.get_frame().set_alpha(0.9)
        else:
            zone_patches = [
                plt.Rectangle((0, 0), 1, 1, fc=specs["color"], alpha=specs["alpha"])
                for specs in zones.values()
            ]
            legend = ax.legend(
                zone_patches,
                [f"{name.title()} Zone" for name in zones.keys()],
                loc="center left",
                bbox_to_anchor=(1.05, 0.5),
                borderaxespad=0,
                frameon=True,
                fancybox=True,
                shadow=True,
            )
            legend.get_frame().set_facecolor("white")
            legend.get_frame().set_alpha(0.9)

    plt.subplots_adjust(right=0.85, hspace=0.3)

    # Save outputs
    output_dir.mkdir(exist_ok=True, parents=True)
    for fmt in ["pdf", "png"]:
        plt.savefig(
            output_dir / f"tree_growth_phase2_zones.{fmt}",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
    plt.close()


def compare_tree_growth(experiment_dir: Path, output_dir: Path):
    """Generate unified visualization showing both phases with consistent styling."""

    # Create figure with all four subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 15), dpi=300)

    # Publication styling
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "axes.linewidth": 1.2,
            "axes.edgecolor": "#333333",
            "grid.alpha": 0.2,
            "font.size": 14,
            "axes.labelsize": 16,
            "axes.titlesize": 18,
            "legend.fontsize": 12,
            "legend.frameon": True,
            "legend.framealpha": 0.9,
            "legend.edgecolor": "#333333",
        }
    )

    # Define complexity zones
    zones = {
        "simple": {"range": (0, 3), "color": "#c8e6c9", "alpha": 0.3},
        "moderate": {"range": (3, 5), "color": "#fff9c4", "alpha": 0.3},
        "complex": {"range": (5, 10), "color": "#ffcdd2", "alpha": 0.3},
    }

    # Plot Phase 1 (with its own depth range)
    max_depth_phase1 = 0
    for model_name, config in models.items():
        metrics_path = (
            experiment_dir / model_name / "average_metrics/phase_1/tree_metrics.json"
        )
        try:
            with open(metrics_path) as f:
                metrics = json.load(f)

            depths = list(map(int, metrics["tree_growth_patterns"].keys()))
            max_depth_phase1 = max(max_depth_phase1, max(depths))
            nodes = list(metrics["tree_growth_patterns"].values())
            cumulative_nodes = np.cumsum(nodes)

            line_style = {
                "marker": "o",
                "label": config["display"],
                "color": config["color"],
                "linewidth": 2.5,
                "markersize": 8,
                "markeredgecolor": "white",
                "markeredgewidth": 1.5,
                "alpha": 0.9,
                "zorder": 3,
            }

            ax1.plot(depths, nodes, **line_style)
            ax3.plot(depths, cumulative_nodes, **line_style)

        except FileNotFoundError:
            print(f"Warning: Phase 1 metrics not found for {model_name}")

    # Plot Phase 2 (maintain colors from phase 1)
    max_depth_phase2 = 0
    for model_name, config in models.items():
        metrics_path = (
            experiment_dir / model_name / "average_metrics/phase_2/tree_metrics.json"
        )
        try:
            with open(metrics_path) as f:
                metrics = json.load(f)

            growth_patterns = metrics["tree_growth_patterns"]
            depths = sorted(map(int, growth_patterns.keys()))
            max_depth_phase2 = max(max_depth_phase2, max(depths))
            nodes = [growth_patterns[str(d)] for d in depths]
            cumulative_nodes = np.cumsum(nodes)

            # Normalize values
            nodes_normalized = [n / sum(nodes) * 100 for n in nodes]
            cumulative_normalized = [
                n / cumulative_nodes[-1] * 100 for n in cumulative_nodes
            ]

            # Use same line style but with updated label for phase 2
            line_style = {
                "marker": "o",
                "label": config["display"],
                "color": config["color"],  # Maintain model-specific color
                "linewidth": 2.5,
                "markersize": 8,
                "markeredgecolor": "white",
                "markeredgewidth": 1.5,
                "alpha": 0.9,
                "zorder": 3,
            }

            ax2.plot(depths, [-n for n in nodes_normalized], **line_style)
            ax4.plot(depths, [-n for n in cumulative_normalized], **line_style)

        except FileNotFoundError:
            print(f"Warning: Phase 2 metrics not found for {model_name}")

    # Set appropriate x-axis limits for each phase
    ax1.set_xlim(0, max_depth_phase1 + 0.15)
    ax3.set_xlim(0, max_depth_phase1 + 0.15)
    ax2.set_xlim(0, max_depth_phase2 + 0.15)
    ax4.set_xlim(0, max_depth_phase2 + 0.15)

    # Configure all subplots
    titles = [
        "Phase 1: Node Expansion Pattern",
        "Phase 2: Node Distribution (%)",
        "Phase 1: Cumulative Tree Growth",
        "Phase 2: Cumulative Distribution (%)",
    ]

    for ax, title in zip([ax1, ax2, ax3, ax4], titles):
        # Add zone shading

        for zone_name, specs in zones.items():
            start, end = specs["range"]
            ax.axvspan(start, end, color=specs["color"], alpha=specs["alpha"], zorder=1)

        ax.set_title(title, pad=20, fontweight="bold")
        ax.set_xlabel("Tree Depth", labelpad=10)
        ax.grid(True, linestyle="--", alpha=0.2, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_facecolor("#F8F9F9")
        ax.tick_params(axis="both", which="major", labelsize=12)

    # Set y-axis labels
    ax1.set_ylabel("Number of Nodes", labelpad=10)
    ax2.set_ylabel("Total Nodes", labelpad=10)
    ax3.set_ylabel("Percentage of Nodes", labelpad=10)
    ax4.set_ylabel("Percentage of Total Nodes", labelpad=10)

    # Invert y-axis for phase 2 plots
    ax2.invert_yaxis()
    ax4.invert_yaxis()

    # Add single legend for all plots
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="center right",
        bbox_to_anchor=(0.98, 0.5),
        borderaxespad=0,
        frameon=True,
        fancybox=True,
        shadow=True,
    )

    # Add zones legend
    zone_patches = [
        plt.Rectangle((0, 0), 1, 1, fc=specs["color"], alpha=specs["alpha"])
        for specs in zones.values()
    ]
    fig.legend(
        zone_patches,
        [f"{name.title()} Zone" for name in zones.keys()],
        loc="center right",
        bbox_to_anchor=(0.98, 0.35),
        borderaxespad=0,
        frameon=True,
        fancybox=True,
        shadow=True,
    )

    plt.subplots_adjust(right=0.85, wspace=0.3, hspace=0.3)

    # Save outputs
    output_dir.mkdir(exist_ok=True, parents=True)
    for fmt in ["pdf", "png"]:
        plt.savefig(
            output_dir / f"tree_growth.{fmt}",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
    plt.close()


def mcts_analysis(experiment_dir: Path, output_dir: Path):
    """Generate two-panel visualization with improved AUC visibility and legend placement."""

    # Set up publication-quality styling
    plt.style.use("seaborn-v0_8-paper")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 14,
            "axes.labelsize": 24,  # Increased from 16
            "axes.titlesize": 28,  # Increased from 18
            "legend.fontsize": 16,  # Increased from 12
            "xtick.labelsize": 20,  # Added for larger tick labels
            "ytick.labelsize": 20,  # Added for larger tick labels
            "axes.labelweight": "bold",  # Added to make all axis labels bold
            "figure.dpi": 300,
        }
    )

    # Create figure with two subplots and extra space for legend
    fig = plt.figure(figsize=(24, 5))
    gs = plt.GridSpec(1, 3, width_ratios=[0.1, 1, 1], wspace=0.7)

    # Create legend axis
    legend_ax = fig.add_subplot(gs[0])
    legend_ax.axis("off")

    # Create main plot axes
    ax1 = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[2])
    ax1_cumulative = ax1.twinx()
    # ax2_cumulative = ax2.twinx()

    # Store legend handles and labels

    # Plot Phase 1
    for model_name, config in models.items():
        metrics_path = (
            experiment_dir / model_name / "average_metrics/phase_1/tree_metrics.json"
        )
        try:
            with open(metrics_path) as f:
                metrics = json.load(f)

            depths = list(map(int, metrics["tree_growth_patterns"].keys()))[1:]
            nodes = list(metrics["tree_growth_patterns"].values())[1:]
            cumulative = np.cumsum(nodes)
            depths = np.array(depths)
            nodes = np.array(nodes)

            if len(depths) > 3:  # Only smooth if we have enough points
                # Create a higher resolution x-axis for smoother curve
                depths_smooth = np.linspace(depths.min(), depths.max(), 300)

                # Create the spline function
                spl = make_interp_spline(depths, nodes, k=2)  # k=3 gives cubic spline

                # Generate smooth curve
                nodes_smooth = spl(depths_smooth)

                # Plot smooth line
                ax1.plot(
                    depths_smooth,
                    nodes_smooth,
                    color=config["color"],
                    linestyle=config["linestyle"],
                    label=f"{config['display']} (per level)",
                    linewidth=2.5,
                    zorder=3,
                )

                # Add original points
                ax1.scatter(
                    depths,
                    nodes,
                    color=config["color"],
                    s=50,
                    zorder=4,
                )
            else:
                # If too few points, plot original
                ax1.plot(
                    depths,
                    nodes,
                    color=config["color"],
                    linestyle=config["linestyle"],
                    label=f"{config['display']} (per level)",
                    linewidth=2.5,
                    marker="o",
                    markersize=6,
                    zorder=3,
                )

            # For cumulative, use same smoothing
            if len(depths) > 3:
                cumulative_smooth = spl.antiderivative()(depths_smooth)
                # Normalize to match original cumulative values
                scale_factor = cumulative[-1] / cumulative_smooth[-1]
                cumulative_smooth *= scale_factor

                ax1_cumulative.fill_between(
                    depths_smooth,
                    cumulative_smooth,
                    alpha=config["auc_alpha"],
                    color=config["color"],
                    label=f"{config['display']} (cumulative)",
                    zorder=2,
                )

                ax1_cumulative.plot(
                    depths_smooth,
                    cumulative_smooth,
                    color=config["color"],
                    linestyle=config["linestyle"],
                    alpha=0.5,
                    linewidth=1.5,
                    zorder=2,
                )
            else:
                # Original plotting for few points
                ax1_cumulative.fill_between(
                    depths,
                    cumulative,
                    alpha=config["auc_alpha"],
                    color=config["color"],
                    label=f"{config['display']} (cumulative)",
                    zorder=2,
                )

        except FileNotFoundError:
            print(f"Warning: Phase 1 metrics not found for {model_name}")

    # Plot Phase 2
    for model_name, config in models.items():
        metrics_path = (
            experiment_dir / model_name / "average_metrics/phase_2/tree_metrics.json"
        )
        try:
            with open(metrics_path) as f:
                metrics = json.load(f)

            depths = sorted(map(int, metrics["tree_growth_patterns"].keys()))
            nodes = [metrics["tree_growth_patterns"][str(d)] for d in depths]
            depths = np.array(depths)
            nodes = np.array(nodes)

            # Calculate total nodes at each depth across all models
            if not hasattr(mcts_analysis, "total_nodes_by_depth"):
                mcts_analysis.total_nodes_by_depth = defaultdict(float)
                for m_name, m_config in models.items():
                    try:
                        with open(
                            experiment_dir
                            / m_name
                            / "average_metrics/phase_2/tree_metrics.json"
                        ) as f:
                            m_metrics = json.load(f)
                            for d, n in m_metrics["tree_growth_patterns"].items():
                                mcts_analysis.total_nodes_by_depth[int(d)] += n
                    except FileNotFoundError:
                        continue

            # Calculate ratio of nodes to total nodes at each depth
            total_nodes = np.array(
                [mcts_analysis.total_nodes_by_depth[d] for d in depths]
            )
            node_ratios = nodes / total_nodes

            # Create smoothed line
            if len(depths) > 3:  # Only smooth if we have enough points
                # Create a higher resolution x-axis for smoother curve
                depths_smooth = np.linspace(depths.min(), depths.max(), 300)

                # Create the spline function for ratios
                spl = make_interp_spline(depths, node_ratios, k=2)

                # Generate smooth curves
                ratios_smooth = spl(depths_smooth)

                # Plot smooth line
                ax2.plot(
                    depths_smooth,
                    ratios_smooth,
                    color=config["color"],
                    linestyle=config["linestyle"],
                    linewidth=2.5,
                    zorder=3,
                )

                # Add original points
                ax2.scatter(
                    depths,
                    node_ratios,
                    color=config["color"],
                    s=50,
                    zorder=4,
                )

            else:
                # Original plotting for few points
                ax2.plot(
                    depths,
                    node_ratios,
                    color=config["color"],
                    linestyle=config["linestyle"],
                    linewidth=2.5,
                    marker="o",
                    markersize=6,
                    zorder=3,
                )

        except FileNotFoundError:
            print(f"Warning: Phase 2 metrics not found for {model_name}")

    # Customize axes
    ax1.set_title("Phase 1", pad=20)
    ax1.set_xlabel("Tree Depth")
    ax1.set_ylabel("Number of Nodes per Depth", labelpad=10)
    ax1_cumulative.set_ylabel("Cumulative Nodes", labelpad=10)
    ax1.grid(True, alpha=0.3, zorder=0)

    ax2.set_title("Phase 2", pad=20)
    ax2.set_xlabel("Tree Depth")
    ax2.set_ylabel("Ratio of Nodes per Depth", labelpad=10)
    ax2.grid(True, alpha=0.3, zorder=0)

    # Create unified legend
    legend_handles = []
    legend_labels = []

    # Add model lines
    for config in models.values():
        legend_handles.append(
            plt.Line2D(
                [0],
                [0],
                color=config["color"],
                linestyle=config["linestyle"],
                linewidth=2.5,
                marker="o",
            )
        )
        legend_labels.append(config["display"] )

    # Add cumulative areas
    for config in models.values():
        legend_handles.append(
            plt.Rectangle((0, 0), 1, 1, fc=config["color"], alpha=config["auc_alpha"])
        )
        legend_labels.append(f"{config['display']} (cumulative)")

    # Place legend in the leftmost subplot with tighter spacing and line breaks
    legend_labels = [label.replace(" ", "\n") for label in legend_labels]
    legend_ax.legend(
        legend_handles,
        legend_labels,
        loc="center",
        bbox_to_anchor=(0.5, 0.5),
        frameon=True,
        edgecolor="black",
        fancybox=True,
        shadow=True,
        handletextpad=1.5,
        borderpad=1.2,
        labelspacing=1.2,
    )

    plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])

    # Save outputs
    output_dir.mkdir(exist_ok=True, parents=True)
    for fmt in ["pdf", "png", "svg"]:
        plt.savefig(
            output_dir / f"mcts_analysis.{fmt}",
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
    plt.close()


if __name__ == "__main__":
    experiment_dir = Path("/Users/ahvra/Nexus/Prism/experiments")
    output_dir = experiment_dir / "comparative_analysis"
    compare_tree_growth(experiment_dir, output_dir)  # Only call unified version
    mcts_analysis(experiment_dir, output_dir)
