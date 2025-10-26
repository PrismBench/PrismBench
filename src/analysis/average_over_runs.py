import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_numeric(value: Any) -> bool:
    """Check if a value is numeric (int or float)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def recursive_deep_merge_and_average(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Recursively merge and average multiple JSON dictionaries.

    Args:
        data_list: List of dictionaries to merge and average

    Returns:
        Dictionary with averaged numeric values and merged structure
    """
    if not data_list:
        return {}

    # Collect all unique keys across all dictionaries
    all_keys = set()
    for data in data_list:
        if isinstance(data, dict):
            all_keys.update(data.keys())

    result = {}

    for key in all_keys:
        # Collect values for this key from all dictionaries
        values = []
        for data in data_list:
            if isinstance(data, dict):
                values.append(data.get(key, 0))  # Use 0 for missing keys
            else:
                values.append(0)

        # Determine how to handle this key based on the values
        if all(is_numeric(v) for v in values):
            # All numeric - calculate average
            result[key] = sum(values) / len(values)
        elif all(isinstance(v, dict) for v in values):
            # All dictionaries - recursively merge
            result[key] = recursive_deep_merge_and_average(values)
        elif all(isinstance(v, list) for v in values):
            # All lists - handle list averaging
            result[key] = average_list_structures(values)
        else:
            # Mixed types or other types - try to handle intelligently
            result[key] = handle_mixed_types(values)

    return result


def average_list_structures(list_values: List[List[Any]]) -> Any:
    """
    Average list structures, handling different list lengths and types.

    Args:
        list_values: List of lists to average

    Returns:
        For numeric lists: single average value of all concatenated numbers
        For other lists: element-wise averaged list structure
    """
    if not list_values:
        return []

    # Check if all lists contain only numeric values
    all_numeric_lists = all(all(is_numeric(item) for item in lst) for lst in list_values if isinstance(lst, list))

    if all_numeric_lists:
        # Concatenate all numeric lists and return the overall average
        all_numbers = []
        for lst in list_values:
            if isinstance(lst, list):
                all_numbers.extend(lst)

        if all_numbers:
            return sum(all_numbers) / len(all_numbers)
        else:
            return 0

    # For non-numeric lists, do element-wise averaging
    # Find the maximum length to handle lists of different sizes
    max_length = max(len(lst) for lst in list_values if isinstance(lst, list))

    result = []
    for i in range(max_length):
        # Collect values at position i from all lists
        position_values = []
        for lst in list_values:
            if isinstance(lst, list) and i < len(lst):
                position_values.append(lst[i])
            else:
                position_values.append(0)  # Use 0 for missing positions

        # Average the values at this position
        if all(is_numeric(v) for v in position_values):
            result.append(sum(position_values) / len(position_values))
        elif all(isinstance(v, dict) for v in position_values):
            result.append(recursive_deep_merge_and_average(position_values))
        else:
            result.append(handle_mixed_types(position_values))

    return result


def handle_mixed_types(values: List[Any]) -> Any:
    """
    Handle mixed types by attempting intelligent merging.

    Args:
        values: List of mixed-type values

    Returns:
        Best-effort merged value
    """
    # Filter out zeros (our missing value indicator)
    non_zero_values = [v for v in values if v != 0]

    if not non_zero_values:
        return 0

    # If we have numeric values, average them
    numeric_values = [v for v in non_zero_values if is_numeric(v)]
    if numeric_values:
        return sum(numeric_values) / len(numeric_values)

    # If we have dictionaries, merge them
    dict_values = [v for v in non_zero_values if isinstance(v, dict)]
    if dict_values:
        return recursive_deep_merge_and_average(dict_values)

    # Otherwise, take the first non-zero value
    return non_zero_values[0]


def load_json_files(directory: str) -> Dict[str, Any]:
    """
    Load all JSON files from a directory.

    Args:
        directory: Path to directory containing JSON files

    Returns:
        Dictionary mapping filename to JSON content
    """
    json_data = {}

    with open(directory, "r") as f:
        json_data = json.load(f)
        logger.info(f"Loaded {directory}")

    return json_data


def average_json_files_across_runs(
    files: List[Path],
) -> Dict[str, Dict[str, Any]]:
    """
    Average JSON files across multiple runs.

    Args:
        base_directory: Base directory containing run directories
        run_pattern: Glob pattern to match run directories
        subdir: Subdirectory within each run containing JSON files

    Returns:
        Dictionary mapping JSON filename to averaged content
    """
    # Find all run directories

    # Collect all JSON files from all runs
    all_json_files = defaultdict(list)

    for file in files:
        json_data = load_json_files(file)

        for filename, content in json_data.items():
            all_json_files[filename].append(content)

    # Average each JSON file type across runs
    averaged_results = {}

    for filename, content_list in all_json_files.items():
        logger.info(f"Averaging {filename} across {len(content_list)} runs")
        averaged_results[filename] = recursive_deep_merge_and_average(content_list)

    return averaged_results


def save_averaged_results(averaged_results: Dict[str, Dict[str, Any]], output_directory: Path) -> None:
    """
    Save averaged results to JSON files.

    Args:
        averaged_results: Dictionary mapping filename to averaged content
        output_directory: Directory to save averaged results
    """
    output_directory.mkdir(parents=True, exist_ok=True)

    for filename, content in averaged_results.items():
        output_path = output_directory / f"averaged_{filename}"

        try:
            with open(output_path, "w") as f:
                json.dump(content, f, indent=2)
            logger.info(f"Saved averaged results to {output_path}")
        except Exception as e:
            logger.error(f"Error saving {output_path}: {e}")


def main() -> None:
    """Main function to run the averaging script."""
    # Example usage - you can modify these paths

    files = [
        "/PrismBench/experiments/old/deepseekv3/final-1/whole_tree_analysis/tree_metrics.json",
        "/PrismBench/experiments/old/deepseekv3/final-2/whole_tree_analysis/tree_metrics.json",
        "/PrismBench/experiments/old/deepseekv3/final-3/whole_tree_analysis/tree_metrics.json",
    ]
    # Average the JSON files
    averaged_results = average_json_files_across_runs(files)

    # Save results
    with open("averaged_results.json", "w") as f:
        json.dump(averaged_results, f, indent=2)


if __name__ == "__main__":
    main()
