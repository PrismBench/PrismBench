import json
from typing import Dict, List


def load_model_data(analysis_file: str) -> Dict:
    """Load model progression data from the comparative analysis file."""
    with open(analysis_file, "r") as f:
        data = json.load(f)
    return data["model_progression"]


def calculate_capability_metrics(
    model_data: Dict,
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """Calculate capability metrics for each concept across difficulties.

    Returns:
        Dict mapping concepts to their metrics for each difficulty category
        Includes failure rates and operational indicators
    """
    concept_metrics = {}

    # Get all difficulties and their data
    difficulties = model_data["performance_by_difficulty"]

    # Initialize tracking for each concept
    all_concepts = set()
    for diff_data in difficulties.values():
        all_concepts.update(diff_data["concepts"].keys())

    # Map difficulty levels to categories
    difficulty_mapping = {
        "very easy": "easy",
        "easy": "easy",
        "medium": "medium",
        "hard": "hard",
        "very hard": "hard",
    }

    # Calculate metrics for each concept
    for concept in all_concepts:
        rates = {
            "easy": {"weighted_sum": 0, "total_weight": 0, "operational": False},
            "medium": {"weighted_sum": 0, "total_weight": 0, "operational": False},
            "hard": {"weighted_sum": 0, "total_weight": 0, "operational": False},
        }

        # Track the highest difficulty attempted
        highest_difficulty = None

        for diff, diff_data in difficulties.items():
            category = difficulty_mapping[diff]
            if concept in diff_data["concepts"]:
                weight = diff_data["concepts"][concept]
                failure_rate = 1 - diff_data["success_rate"]
                rates[category]["weighted_sum"] += failure_rate * weight
                rates[category]["total_weight"] += weight
                highest_difficulty = category

        # Mark operational difficulty level
        if highest_difficulty:
            rates[highest_difficulty]["operational"] = True

        # Calculate final metrics
        concept_metrics[concept] = {}
        for category, data in rates.items():
            if data["total_weight"] > 0:
                failure_rate = data["weighted_sum"] / data["total_weight"]
            else:
                # If never attempted at this level, check if it's due to mastery or inability
                if highest_difficulty:
                    difficulty_order = ["easy", "medium", "hard"]
                    current_idx = difficulty_order.index(category)
                    highest_idx = difficulty_order.index(highest_difficulty)
                    failure_rate = 0.0 if current_idx < highest_idx else 1.0
                else:
                    failure_rate = 1.0

            concept_metrics[concept][category] = {
                "failure_rate": failure_rate,
                "operational": data["operational"],
            }

    return concept_metrics


def generate_latex_table(
    model_metrics: Dict[str, Dict[str, Dict[str, float]]], model_names: List[str]
) -> str:
    """Generate a LaTeX table comparing concept capabilities across models."""
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
        "\\caption{Model Capability Analysis by Concept and Difficulty}",
        "\\label{tab:concept-capabilities}",
        # Each difficulty level gets its own column for each model
        "\\begin{tabular}{l" + ("c|" * (len(sorted_models) - 1) + "c ") * 3 + "}",
        "\\toprule",
    ]

    # Add difficulty level headers
    latex.append(
        f"& \\multicolumn{{{len(sorted_models)}}}{{c}}{{Easy}} & "
        f"\\multicolumn{{{len(sorted_models)}}}{{c}}{{Medium}} & "
        f"\\multicolumn{{{len(sorted_models)}}}{{c}}{{Hard}} \\\\"
    )

    # Add cmidrules
    cmidrules = []
    for i in range(3):
        start = i * len(sorted_models) + 2
        end = start + len(sorted_models) - 1
        cmidrules.append(f"\\cmidrule(lr){{{start}-{end}}}")
    latex.append(" ".join(cmidrules))

    # Add model headers
    model_headers = []
    for _ in range(3):
        for model in sorted_models:
            model_headers.append(model_name_map[model])
    latex.append("\\textbf{Concept} & " + " & ".join(model_headers) + "\\\\")
    latex.append("\\midrule")

    def get_cell_format(metrics: Dict[str, float]) -> str:
        """Generate cell format based on metrics."""
        if metrics["failure_rate"] == 0.0:
            return "\\cellcolor{goodgreen!25}\\checkmark"  # Mastered
        if metrics["failure_rate"] == 1.0:
            return "-"  # Never attempted/Beyond capability

        failure_rate = metrics["failure_rate"]
        operational = metrics["operational"]

        # Color intensity based on failure rate
        if failure_rate <= 0.3:
            intensity = 25 + (failure_rate / 0.3) * 35
            color = f"goodgreen!{int(intensity)}"
        elif failure_rate <= 0.6:
            intensity = 30 + ((failure_rate - 0.3) / 0.3) * 40
            color = f"midyellow!{int(intensity)}"
        else:
            intensity = 40 + ((failure_rate - 0.6) / 0.4) * 50
            color = f"badred!{int(intensity)}"

        # Add operational indicator if this is the primary difficulty level
        value = f"{failure_rate:.2f}"
        if operational:
            value += "†"

        return f"\\cellcolor{{{color}}}{value}"

    # Add data rows
    all_concepts = sorted(concept_names.keys())
    for concept in all_concepts:
        row = [concept_names[concept]]
        for difficulty in ["easy", "medium", "hard"]:
            for model in sorted_models:
                if model in model_metrics and concept in model_metrics[model]:
                    metrics = model_metrics[model][concept][difficulty]
                    row.append(get_cell_format(metrics))
                else:
                    row.append("-")
        latex.append(" & ".join(row) + "\\\\[\\smallskipamount]")

    # Add footer
    latex.extend(
        [
            "\\bottomrule",
            "\\multicolumn{"
            + str(3 * len(sorted_models) + 1)
            + "}{@{}p{\\linewidth}}{",
            "\\footnotesize Note: Values represent failure rates (higher = more challenging). ",
            "Colors indicate performance: green (good) to red (poor). ",
            "† indicates primary operational difficulty level. ",
            "\\checkmark indicates mastered concepts. ",
            "- indicates concepts beyond current capability. ",
            "Model abbreviations: "
            + ", ".join([f"{v}={k}" for k, v in model_name_map.items()])
            + "}",
            "\\end{tabular}",
            "\\end{table*}",
        ]
    )

    return "\n".join(latex)


def main():
    # File paths
    analysis_file = (
        "/Users/ahvra/Nexus/Prism/analysis_results/comparative_analysis.json"
    )
    output_file = "analysis_results/concept_capability_table.tex"

    # Load and process data
    raw_data = load_model_data(analysis_file)

    # Calculate capability metrics for each model
    model_metrics = {}
    for model_name, model_data in raw_data.items():
        model_metrics[model_name] = calculate_capability_metrics(model_data)

    # Generate table
    latex_table = generate_latex_table(model_metrics, list(raw_data.keys()))

    # Save to file
    with open(output_file, "w") as f:
        f.write(latex_table)

    print(f"Table saved to {output_file}")


if __name__ == "__main__":
    main()
