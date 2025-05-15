from typing import Dict
import json
import pandas as pd
from pathlib import Path


def accumulate_data(aggregator, data):
    """Accumulate nested dictionaries into aggregator, treating missing as zero."""
    for key, val in data.items():
        if isinstance(val, dict):
            if key not in aggregator:
                aggregator[key] = {}
            accumulate_data(aggregator[key], val)
        elif isinstance(val, (int, float)):
            if key not in aggregator:
                aggregator[key] = {"sum": 0.0, "count": 0}
            aggregator[key]["sum"] += val
            aggregator[key]["count"] += 1
        elif isinstance(val, list):
            # Handle lists of dictionaries or numbers
            if len(val) > 0 and isinstance(val[0], dict):
                # Check if we have a 'difficulty' key
                if "difficulty" in val[0]:
                    if key not in aggregator:
                        aggregator[key] = {}
                    for item in val:
                        difficulty = item.get("difficulty", "_none_")
                        if difficulty not in aggregator[key]:
                            aggregator[key][difficulty] = {}
                        accumulate_data(aggregator[key][difficulty], item)
                else:
                    # Index-based dict accumulation
                    if key not in aggregator:
                        aggregator[key] = []
                    # Accumulate each dict in the list separately
                    while len(aggregator[key]) < len(val):
                        aggregator[key].append({})
                    for i, item in enumerate(val):
                        if isinstance(item, dict):
                            accumulate_data(aggregator[key][i], item)
            elif len(val) > 0 and isinstance(val[0], (int, float)):
                # Sum numeric lists
                if key not in aggregator:
                    aggregator[key] = {"sum": 0.0, "count": 0}
                aggregator[key]["sum"] += sum(val)
                aggregator[key]["count"] += len(val)
            else:
                # Lists of other types - do nothing or customize if needed
                pass
        else:
            # For lists or other structures, handle as needed or leave unchanged
            pass


def finalize_averages(aggregator):
    """Compute averages from the aggregator, recursively."""
    result = {}
    for key, val in aggregator.items():
        if isinstance(val, dict) and "sum" in val and "count" in val:
            # It's a numeric aggregator
            if val["count"] == 0:
                result[key] = 0
            else:
                result[key] = val["sum"] / 3
        elif isinstance(val, dict):
            # Recurse deeper
            result[key] = finalize_averages(val)
        else:
            result[key] = val
    return result


def read_and_structure_metrics(experiment_dir: Path, models: list):
    """Read total_validation_issues from each model's test_metrics.json and structure them into a DataFrame."""
    all_data = {}

    for model in models:
        metrics_path = (
            experiment_dir / model / "average_metrics/phase_3/test_metrics.json"
        )
        if not metrics_path.exists():
            print(f"Warning: Missing test metrics file for {model}")
            continue

        with open(metrics_path) as f:
            data = json.load(f)
            total_validation_issues = data.get("validation_distributions", {})
            for issue, value in total_validation_issues.items():
                if issue not in all_data:
                    all_data[issue] = {}
                all_data[issue][model] = value

    return pd.DataFrame(all_data).transpose().reset_index()


def generate_tier_detail(data):

    # Rename the first column for clarity
    data.rename(columns={data.columns[0]: "concept_combination"}, inplace=True)

    # Calculate the "tier" based on the number of concepts in each combination
    data["tier"] = data["concept_combination"].apply(
        lambda x: f"Tier {len(x.split('-'))}"
    )

    # Extract model columns (everything except 'concept_combination' and 'tier')
    model_columns = [
        col for col in data.columns if col not in ["concept_combination", "tier"]
    ]

    # Define a function to parse and sum errors from dictionary strings
    def parse_and_sum_errors(error_entry):
        """
        Parses the error dictionary string and sums its values.
        If the entry is invalid or not a dictionary, it returns 0.
        """
        try:
            # error_dict = eval(error_entry)  # Parse the string to a dictionary
            return sum(error_entry.values()) if isinstance(error_entry, dict) else 0
        except (SyntaxError, TypeError):
            return 0

    # Initialize summary storage
    summary = {}

    for model in model_columns:
        model_data = data[~data[model].isna()]  # Rows where the model has data
        tiers = model_data["tier"].unique()  # Tiers where the model has entries

        tier_summary = {}
        for tier in tiers:
            tier_data = model_data[model_data["tier"] == tier][model]

            # Count concept combinations
            num_combinations = len(tier_data)

            # Aggregate error metrics
            total_errors = tier_data.apply(parse_and_sum_errors).sum()

            tier_summary[tier] = {
                "num_combinations": num_combinations,
                "total_errors": total_errors,
            }

        # Store model summary
        summary[model] = {
            "tiers": list(tier_summary.keys()),
            "details": tier_summary,
            "high_tier_combos": sum(1 for t in tier_summary if "3" in t or "4" in t),
            "high_tier_errors": sum(
                tier_summary[t]["total_errors"]
                for t in tier_summary
                if "3" in t or "4" in t
            ),
        }

    # Convert summary to a DataFrame for better visualization
    return summary


def generate_latex_table(data: Dict[str, Dict]) -> str:
    """
    Generate a LaTeX table comparing the models across tiers with improved styling.
    
    Args:
        data (Dict[str, Dict]): The input data containing model tier details.
    
    Returns:
        str: The LaTeX table as a string.
    """
    model_display = {
        '4o': '4o',
        'llama3.1-70b': 'L70b',
        'llama3.1-405b': 'L405b',
        '4o-mini': '4o-mini',
        'llama3.1-8b': 'L 8b'
    }

    latex = [
        "\\begin{table}[h]",
        "\\centering",
        "\\caption{Comparison of Models Across Tiers}",
        "\\label{tab:model_comparison}",
        "    \\begin{tabular}{l@{\\hspace{0.5em}}c ccc ccc}",
        "    \\toprule",
        "        & \\multicolumn{3}{c}{\\textbf{\\makecell{\\# of Concepts}}} & \\multicolumn{3}{c}{\\textbf{\\makecell{\\# Test Validation Errors \\\\ per \\# of Concepts}}} \\\\",
        "        \\cmidrule(lr){2-4} \\cmidrule(lr){5-7}",
        "        \\textbf{Model} & \\makecell{2} & \\makecell{3} & \\makecell{4} & \\makecell{2} & \\makecell{3} & \\makecell{4} \\\\",
        "    \\midrule"
    ]

    for model, model_data in data.items():
        details = model_data['details']
        nums = []
        errs = []

        # Get data for each tier
        for tier in ['Tier 2', 'Tier 3', 'Tier 4']:
            if tier in details:
                nums.append(str(details[tier]['num_combinations']))
                errs.append(f"{details[tier]['total_errors']:.2f}")
            else:
                nums.append('0')
                errs.append('0.00')

        # Format the line with additional spacing
        display_name = model_display.get(model, model)
        line = f"        {display_name} & {' & '.join(nums)} & {' & '.join(errs)} \\\\[\\smallskipamount]"
        latex.append(line)

    latex.extend(
        [
            "    \\bottomrule",
            "        \\multicolumn{7}{@{}p{\\linewidth}}{\\footnotesize Note: L: Llama, M: Mini.}",
            "    \\end{tabular}",
            "\\end{table}",
        ]
    )

    return "\n".join(latex)


if __name__ == "__main__":
    experiment_dir = Path("/Users/ahvra/Nexus/Prism/experiments")
    models = ["4o", "4o-mini", "llama3.1-8b", "llama3.1-70b", "llama3.1-405b"]

    df = read_and_structure_metrics(experiment_dir, models)
    summary = generate_tier_detail(df)
    with open("tier_comparison_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    latex_table = generate_latex_table(summary)
    with open("tier_comparison_table.tex", "w") as f:
        f.write(latex_table)
