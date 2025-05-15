import json
from pathlib import Path
from typing import Dict, List


def load_metrics_data(metrics_file: str) -> Dict:
    """Load metrics data from a JSON file."""
    with open(metrics_file, "r") as f:
        data = json.load(f)
    return data


def generate_latex_table_difficulties(
    model_metrics: Dict[str, Dict[str, Dict[str, float]]], model_names: List[str]
) -> str:
    """Generate a LaTeX table comparing performance by difficulty across models."""
    # Map model names to shorter versions
    model_name_map = {
        "4o": "4o",
        "4o-mini": "4o-M",
        "llama3.1-405b": "L405",
        "llama3.1-70b": "L70",
        "llama3.1-8b": "L8",
    }

    # Sort model_names according to model_name_map order
    sorted_models = [model for model in model_name_map.keys() if model in model_names]

    # Start LaTeX table
    latex = [
        "% Required packages:",
        "% \\usepackage[table]{xcolor}",
        "\\begin{table*}[h]",
        "\\centering",
        "\\caption{Model Performance by Difficulty}",
        "\\label{tab:performance-difficulty}",
        "\\begin{tabular}{l" + "c|c" * len(sorted_models) + "}",
        "\\toprule",
    ]

    # Add model headers with subcolumns
    header_row = ["\\textbf{Difficulty}"]
    subheader_row = [""]
    for model in sorted_models:
        header_row.append(f"\\multicolumn{{2}}{{c|}}{{{model_name_map[model]}}}")
        subheader_row.extend(["Avg Succ. Rate", "Avg Inter."])
    latex.append(" & ".join(header_row) + "\\\\")
    latex.append(" & ".join(subheader_row) + "\\\\")
    latex.append("\\midrule")

    # Add data rows
    difficulties = ["very easy", "easy", "medium", "hard", "very hard"]
    for difficulty in difficulties:
        row = [difficulty.capitalize()]
        for model in sorted_models:
            if model in model_metrics:
                metrics = model_metrics[model]
                success_rate = metrics["success_rates_by_difficulty"].get(difficulty, 0)
                interventions = metrics["fixer_intervention_rate_difficulty"].get(difficulty, 0)
                row.extend([f"{success_rate:.2f}", f"{interventions:.2f}"])
            else:
                row.extend(["-", "-"])
        latex.append(" & ".join(row) + "\\\\[\\smallskipamount]")

    # Add footer
    latex.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table*}",
        ]
    )

    return "\n".join(latex)


def generate_latex_table_concepts(
    model_metrics: Dict[str, Dict[str, Dict[str, float]]], model_names: List[str]
) -> str:
    """Generate a LaTeX table comparing performance by concept across models."""
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

    # Map model names to shorter versions
    model_name_map = {
        "4o": "4o",
        "4o-mini": "4o-M",
        "llama3.1-405b": "L405",
        "llama3.1-70b": "L70",
        "llama3.1-8b": "L8",
    }

    # Sort model_names according to model_name_map order
    sorted_models = [model for model in model_name_map.keys() if model in model_names]

    # Start LaTeX table
    latex = [
        "% Required packages:",
        "% \\usepackage[table]{xcolor}",
        "\\begin{table*}[h]",
        "\\centering",
        "\\caption{Model Performance by Concept}",
        "\\label{tab:performance-concept}",
        "\\begin{tabular}{l" + "c|c" * len(sorted_models) + "}",
        "\\toprule",
    ]

    # Add model headers with subcolumns
    header_row = ["\\textbf{Concept}"]
    subheader_row = [""]
    for model in sorted_models:
        header_row.append(f"\\multicolumn{{2}}{{c|}}{{{model_name_map[model]}}}")
        subheader_row.extend(["Avg Succ. Rate", "Avg Inter."])
    latex.append(" & ".join(header_row) + "\\\\")
    latex.append(" & ".join(subheader_row) + "\\\\")
    latex.append("\\midrule")

    # Add data rows
    for concept in concept_names.keys():
        row = [concept_names[concept]]
        for model in sorted_models:
            if model in model_metrics:
                metrics = model_metrics[model]
                success_rate = metrics["success_rates_by_concept"].get(concept, 0)
                interventions = metrics["fixer_intervention_rate_concept"].get(concept, 0)
                row.extend([f"{success_rate:.2f}", f"{interventions:.2f}"])
            else:
                row.extend(["-", "-"])
        latex.append(" & ".join(row) + "\\\\[\\smallskipamount]")

    # Add footer
    latex.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table*}",
        ]
    )

    return "\n".join(latex)


def main():
    # Directory containing metrics JSON files
    metrics_dir = Path("/Users/ahvra/Nexus/Prism/experiments")

    # Load and process data
    model_metrics = {}
    model_names = ["4o", "4o-mini", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]
    for model_name in model_names:
        metrics_file = (
            metrics_dir / f"{model_name}/average_metrics/whole_tree/basic_metrics.json"
        )
        model_metrics[model_name] = load_metrics_data(metrics_file)

    # Generate tables
    latex_table_difficulties = generate_latex_table_difficulties(
        model_metrics, model_names
    )
    latex_table_concepts = generate_latex_table_concepts(model_metrics, model_names)

    # Save to files
    output_file_difficulties = (
        "/Users/ahvra/Nexus/Prism/analysis_results/performance_difficulty_table.tex"
    )
    with open(output_file_difficulties, "w") as f:
        f.write(latex_table_difficulties)

    output_file_concepts = (
        "/Users/ahvra/Nexus/Prism/analysis_results/performance_concept_table.tex"
    )
    with open(output_file_concepts, "w") as f:
        f.write(latex_table_concepts)

    print(f"Tables saved to {output_file_difficulties} and {output_file_concepts}")


if __name__ == "__main__":
    main()
