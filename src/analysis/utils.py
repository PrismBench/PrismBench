import json
from pathlib import Path
from typing import Dict


def save_metrics(metrics: Dict, output_dir: Path, prefix: str = ""):
    """Save metrics to JSON file"""
    metrics = _convert_tuple_keys(metrics)
    output_path = output_dir / f"{prefix}metrics.json"
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=4)


def _convert_tuple_keys(data: Dict) -> Dict:
    """Convert tuple keys to strings for JSON serialization"""
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        # Convert tuple keys to string
        if isinstance(key, tuple):
            new_key = "+".join(key)
        else:
            new_key = key

        # Recursively convert nested dictionaries
        if isinstance(value, dict):
            result[new_key] = _convert_tuple_keys(value)
        else:
            result[new_key] = value
    return result


def setup_output_directories(base_dir: Path) -> Dict[str, Path]:
    """Create and return output directories"""
    directories = {
        "output": base_dir / "whole_tree_analysis",
        "viz": base_dir / "whole_tree_analysis" / "visualizations",
        "basic_metrics": base_dir / "whole_tree_analysis" / "visualizations" / "basic_metrics",
        "concept_metrics": base_dir / "whole_tree_analysis" / "visualizations" / "concept_metrics",
        "tree_metrics": base_dir / "whole_tree_analysis" / "visualizations" / "tree_metrics",
        "test_metrics": base_dir / "whole_tree_analysis" / "visualizations" / "test_metrics",
        "error_metrics": base_dir / "whole_tree_analysis" / "visualizations" / "error_metrics",
        "pattern_metrics": base_dir / "whole_tree_analysis" / "visualizations" / "pattern_metrics",
    }

    for directory in directories.values():
        directory.mkdir(exist_ok=True, parents=True)

    return directories
