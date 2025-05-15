import json
import os


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
                result[key] = val["sum"] / val["count"]
        elif isinstance(val, dict):
            # Recurse deeper
            result[key] = finalize_averages(val)
        else:
            result[key] = val
    return result


def load_and_average_metrics() -> dict:
    """Load all metric JSONs and average them using pandas"""
    models = [
        "4o",
        "4o-mini",
        "llama3.1-8b",
        "llama3.1-70b",
        "llama3.1-405b",
    ]
    phases = ["phase_1", "phase_2", "phase_3", "whole_tree"]
    for model, phase in [(model, phase) for model in models for phase in phases]:

        if phase != "phase_3":
            metrics = ["basic_metrics", "concept_metrics", "tree_metrics"]
        else:
            metrics = ["error_metrics", "pattern_metrics", "test_metrics"]

        for metric in metrics:
            json_files = [
                f"/Users/ahvra/Nexus/Prism/experiments/{model}/final-1/{phase}_analysis/{metric}.json",
                f"/Users/ahvra/Nexus/Prism/experiments/{model}/final-2/{phase}_analysis/{metric}.json",
                f"/Users/ahvra/Nexus/Prism/experiments/{model}/final-3/{phase}_analysis/{metric}.json",
            ]

            aggregator = {}
            for file_path in json_files:
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                    # Accumulate each run's data
                    accumulate_data(aggregator, data)
                except FileNotFoundError:
                    print(f"Warning: Missing {metric} file: {file_path}")
                    continue

            # Convert aggregator sums to final averages
            result = finalize_averages(aggregator)
            if not os.path.exists(
                f"/Users/ahvra/Nexus/Prism/experiments/{model}/average_metrics/{phase}"
            ):
                os.makedirs(
                    f"/Users/ahvra/Nexus/Prism/experiments/{model}/average_metrics/{phase}",
                    exist_ok=True,
                )
            # Save averaged results
            with open(
                f"/Users/ahvra/Nexus/Prism/experiments/{model}/average_metrics/{phase}/{metric}.json",
                "w",
            ) as f:
                json.dump(result, f, indent=4)


if __name__ == "__main__":
    results = load_and_average_metrics()
    print("Averaged metrics saved to averaged_metrics.json")
