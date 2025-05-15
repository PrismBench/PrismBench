import json
from typing import Dict, List


def load_model_data(analysis_file: str) -> Dict:
    """Load model progression data from the comparative analysis file."""
    with open(analysis_file, "r") as f:
        data = json.load(f)
    return data["model_progression"]


def calculate_failure_rates(model_data: Dict) -> Dict[str, Dict[str, float]]:
    """Calculate average failure rates for each concept across difficulties.

    Returns:
        Dict mapping concepts to their failure rates for each difficulty category
    """
    concept_rates = {}

    # Get all difficulties and their success rates
    difficulties = model_data["performance_by_difficulty"]

    # Initialize tracking for each concept
    all_concepts = set()
    for diff_data in difficulties.values():
        all_concepts.update(diff_data["concepts"].keys())

    # Calculate rates for each concept
    for concept in all_concepts:
        rates = {
            "easy": {"weighted_sum": 0, "total_weight": 0},
            "medium": {"weighted_sum": 0, "total_weight": 0},
            "hard": {"weighted_sum": 0, "total_weight": 0},
        }

        for diff in ["very easy", "easy"]:
            if diff in difficulties:
                if concept in difficulties[diff]["concepts"]:
                    weight = difficulties[diff]["concepts"][concept]
                    failure_rate = 1 - difficulties[diff]["success_rate"]
                    rates["easy"]["weighted_sum"] += failure_rate * weight
                    rates["easy"]["total_weight"] += weight

        if "medium" in difficulties:
            if concept in difficulties["medium"]["concepts"]:
                weight = difficulties["medium"]["concepts"][concept]
                failure_rate = 1 - difficulties["medium"]["success_rate"]
                rates["medium"]["weighted_sum"] += failure_rate * weight
                rates["medium"]["total_weight"] += weight

        for diff in ["hard", "very hard"]:
            if diff in difficulties:
                if concept in difficulties[diff]["concepts"]:
                    weight = difficulties[diff]["concepts"][concept]
                    failure_rate = 1 - difficulties[diff]["success_rate"]
                    rates["hard"]["weighted_sum"] += failure_rate * weight
                    rates["hard"]["total_weight"] += weight

        # Calculate averages
        concept_rates[concept] = {
            category: (
                data["weighted_sum"] / data["total_weight"]
                if data["total_weight"] > 0
                else 0
            )
            for category, data in rates.items()
        }

    return concept_rates


def generate_latex_table(
    model_data: Dict[str, Dict[str, Dict[str, float]]], model_names: List[str]
) -> str:
    """Generate a LaTeX table comparing concept performance across models with color coding."""
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

    # Map model names to shorter versions and define order
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
        "\\caption{Concept Performance by Difficulty Level (Failure Rates)}",
        "\\label{tab:concept-performance}",
        # Each number gets its own cell, with extra cells for vertical bars
        "\\begin{tabular}{l"
        + ("c|" * (len(sorted_models) - 1) + "c ") * 2
        + "c|" * (len(sorted_models) - 1)
        + "c"
        + "}",
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

    def get_color_cmd(value: float) -> str:
        """Generate color command based on value."""
        if value is None:
            return ""
        if value == 0.0:
            return "\\cellcolor{goodgreen!25}"  # Keep zeros light green
        if value <= 0.3:
            intensity = 25 + (value / 0.3) * 35  # Scale from 25% to 60%
            return f"\\cellcolor{{goodgreen!{int(intensity)}}}"
        elif value <= 0.6:
            intensity = 30 + ((value - 0.3) / 0.3) * 40  # Scale from 30% to 70%
            return f"\\cellcolor{{midyellow!{int(intensity)}}}"
        else:
            intensity = 40 + ((value - 0.6) / 0.4) * 50  # Scale from 40% to 90%
            return f"\\cellcolor{{badred!{int(intensity)}}}"

    # Add data rows
    all_concepts = sorted(concept_names.keys())
    for concept in all_concepts:
        row = [concept_names[concept]]
        for difficulty in ["easy", "medium", "hard"]:
            for model in sorted_models:
                if model in model_data and concept in model_data[model]:
                    value = model_data[model][concept][difficulty]
                    color_cmd = get_color_cmd(value)
                    row.append(f"{color_cmd}{value:.2f}")
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
            "\\footnotesize Note: Values represent failure rates (1 - success rate). ",
            "Colors indicate performance: green (good) to red (poor). ",
            "Model abbreviations: "
            + ", ".join([f"{v}={k}" for k, v in model_name_map.items()])
            + ". ",
            "Missing values (-) indicate no attempts at that difficulty level.}",
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
    output_file = "analysis_results/concept_performance_table.tex"

    # Load and process data
    raw_data = load_model_data(analysis_file)

    # Calculate failure rates for each model
    model_rates = {}
    for model_name, model_data in raw_data.items():
        model_rates[model_name] = calculate_failure_rates(model_data)

    # Generate table
    latex_table = generate_latex_table(model_rates, list(raw_data.keys()))

    # Save to file
    with open(output_file, "w") as f:
        f.write(latex_table)

    print(f"Table saved to {output_file}")


if __name__ == "__main__":
    main()
