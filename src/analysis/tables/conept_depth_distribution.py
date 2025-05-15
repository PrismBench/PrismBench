import json
import numpy as np
from typing import Dict, List, Tuple
import os


def load_model_data(phase_paths: Dict[str, Tuple[str, str]]) -> Dict[str, Dict]:
    """Load concept distribution data for each model from both phases."""
    model_data = {}
    for model_name, (phase1_path, phase2_path) in phase_paths.items():
        # Load Phase 1 data
        with open(phase1_path, "r") as f:
            phase1_data = json.load(f)
            phase1_dist = phase1_data["concept_depth_distribution"]

        # Load Phase 2 data
        with open(phase2_path, "r") as f:
            phase2_data = json.load(f)
            phase2_dist = phase2_data["concept_depth_distribution"]

        # Combine phase data
        combined_dist = {
            "phase_1": {},
            "phase_2": {},
        }
        for concept in phase1_dist.keys():
            combined_dist["phase_1"][concept] = {}
            combined_dist["phase_2"][concept] = {}
            # Phase 1 depths
            for depth, value in phase1_dist[concept].items():
                combined_dist["phase_1"][concept][depth] = value
            # Phase 2 depths
            for depth, value in phase2_dist[concept].items():
                new_depth = int(depth)
                combined_dist["phase_2"][concept][str(new_depth)] = value

        model_data[model_name] = combined_dist

    return model_data


def count_total_nodes_per_depth(data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Count total number of nodes at each depth across all concepts.

    Args:
        data: Dictionary of concept distributions

    Returns:
        Dictionary mapping depth to total node count
    """
    depth_totals = {}

    # Iterate through each concept
    for concept, depths in data.items():
        # For each depth in this concept
        for depth, count in depths.items():
            if depth not in depth_totals:
                depth_totals[depth] = 0
            depth_totals[depth] += count

    # Sort by depth
    return dict(sorted(depth_totals.items(), key=lambda x: int(x[0])))


# Example usage:
# total_nodes = count_total_nodes_per_depth(concept_distribution)
def calculate_depth_ranges(data: Dict, depth_ranges: List[List[int]]) -> Dict:
    """Calculate average values for specified depth ranges for each phase.

    Args:
        data: Dictionary with phase_1 and phase_2 concept distributions
        depth_ranges: List of depth range pairs to calculate averages for

    Returns:
        Dictionary with phase-specific averages for each concept
    """
    phase_averages = {
        "phase_1": {},
        "phase_2": {},
    }

    # Process each phase separately
    for phase in ["phase_1", "phase_2"]:
        phase_data = data[phase]
        total_nodes_per_depth = count_total_nodes_per_depth(phase_data)

        for concept, depths in phase_data.items():
            if concept not in phase_averages[phase]:
                phase_averages[phase][concept] = []

            # Only process relevant ranges for each phase
            relevant_ranges = (
                depth_ranges[:2] if phase == "phase_1" else depth_ranges[2:]
            )
            for start, end in relevant_ranges:
                values = []
                for d in range(start, end + 1):
                    if str(d) in depths:
                        values.append(
                            depths[str(d)] / total_nodes_per_depth[str(d)] * 100
                        )
                avg = np.mean(values) if values else 0
                phase_averages[phase][concept].append(round(avg, 1))

    return phase_averages


def calculate_phase_percentages(data: Dict) -> Dict:
    """Calculate percentage of nodes in each phase for each concept.

    Args:
        data: Dictionary with phase_1 and phase_2 concept distributions

    Returns:
        Dictionary with phase percentages for each concept
    """
    phase_percentages = {
        "phase_1": {},
        "phase_2": {},
    }

    # Process each phase separately
    for phase in ["phase_1", "phase_2"]:
        phase_data = data[phase]
        total_nodes = sum(
            sum(depths.values())
            for concept_depths in phase_data.values()
            for depths in [concept_depths]
        )

        for concept, depths in phase_data.items():
            concept_nodes = sum(depths.values())
            percentage = (concept_nodes / total_nodes * 100) if total_nodes > 0 else 0
            phase_percentages[phase][concept] = round(percentage, 1)

    return phase_percentages


def generate_latex_table(model_data: Dict[str, Dict], model_names: List[str]) -> str:
    """Generate a LaTeX table with clean formatting and grouped headers."""
    # Calculate percentages for each model
    model_percentages = {}
    for model, data in model_data.items():
        model_percentages[model] = calculate_phase_percentages(data)

    # Start LaTeX table with improved formatting
    latex = [
        "\\begin{table}[h]",
        "\\centering",
        "\\caption{Concept Distribution Analysis by Phase}",
        "\\label{tab:concept-distribution}",
        "\\resizebox{\\linewidth}{!}{%",
        "\\begin{tabular}{l@{\\hspace{2em}}cc|cc}",
        "\\toprule",
        "& \\multicolumn{2}{c}{Phase 1} & \\multicolumn{2}{c}{Phase 2} \\\\",
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}",
        "Concept & M & L & M & L \\\\",
        "\\midrule",
    ]

    # Map full names for concepts
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

    def format_value(val: float) -> str:
        """Format a value with consistent spacing."""
        return f"{val:4.1f}"

    # Add data rows with proper formatting
    concepts = sorted(model_percentages[model_names[0]]["phase_1"].keys())
    for concept in concepts:
        row_values = []

        # Phase 1
        model1_p1 = model_percentages[model_names[0]]["phase_1"][concept]
        model2_p1 = model_percentages[model_names[1]]["phase_1"][concept]
        row_values.extend([format_value(model1_p1), format_value(model2_p1)])

        # Phase 2
        model1_p2 = model_percentages[model_names[0]]["phase_2"][concept]
        model2_p2 = model_percentages[model_names[1]]["phase_2"][concept]
        row_values.extend([format_value(model1_p2), format_value(model2_p2)])

        # Add row to table
        display_name = concept_names.get(concept, concept)
        latex.append(f"{display_name} & {' & '.join(row_values)}\\\\")

    # Add footer
    latex.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "}",  # Close resizebox
            "\\\\[1em]",  # Add some space before the note
            "\\footnotesize Note: Values represent the percentage of nodes in each phase.",
            "\\footnotesize M = GPT-4, L = LLaMA 3.1 (405B).",
            "\\end{table}",
        ]
    )

    return "\n".join(latex)


def main():
    # Base paths for each model
    base_dir = "/Users/ahvra/Nexus/Prism/experiments"
    models = {
        "4o": "4o",
        "L3.1-405b": "llama3.1-405b",  # Assuming this is the correct directory for L3.1-70b
    }

    # Construct paths for each model's phase files
    phase_paths = {}
    for model_name, model_dir in models.items():
        phase1_path = os.path.join(
            base_dir, model_dir, "average_metrics/phase_1/tree_metrics.json"
        )
        phase2_path = os.path.join(
            base_dir, model_dir, "average_metrics/phase_2/tree_metrics.json"
        )
        phase_paths[model_name] = (phase1_path, phase2_path)

    # Load data and generate table
    model_data = load_model_data(phase_paths)
    latex_table = generate_latex_table(model_data, list(models.keys()))

    # Save to file
    output_path = os.path.join(base_dir, "concept_distribution_table.tex")
    with open(output_path, "w") as f:
        f.write(latex_table)

    print(f"Table saved to {output_path}")


if __name__ == "__main__":
    main()
