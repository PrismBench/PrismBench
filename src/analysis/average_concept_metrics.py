#!/usr/bin/env python3
"""Script to average concept metrics across multiple runs with difficulty level grouping."""

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_concept_metrics(file_path: Path) -> Dict[str, Any]:
    """
    Load concept metrics from a JSON file.

    Args:
        file_path: Path to the concept metrics JSON file

    Returns:
        The concept_mastery_distribution data from the JSON file

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
        KeyError: If concept_mastery_distribution key is missing
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        if "concept_mastery_distribution" not in data:
            raise KeyError(f"'concept_mastery_distribution' key not found in {file_path}")

        logger.info(f"Loaded concept metrics from {file_path}")
        return data["concept_mastery_distribution"]

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise
    except KeyError as e:
        logger.error(f"Missing key in {file_path}: {e}")
        raise


def group_difficulty_levels(concept_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Group difficulty levels and combine them according to the specified rules.

    Groups:
    - "easy": combines "very easy" + "easy"
    - "medium": keeps "medium"
    - "hard": combines "hard" + "very hard"

    Args:
        concept_data: List of difficulty level dictionaries for a concept

    Returns:
        Dictionary with grouped difficulty levels and their aggregated metrics
    """
    # Group the raw data by difficulty level
    difficulty_groups = {"easy": [], "medium": [], "hard": []}

    for item in concept_data:
        difficulty = item.get("difficulty", "").lower()

        if difficulty in ["very easy", "easy"]:
            difficulty_groups["easy"].append(item)
        elif difficulty == "medium":
            difficulty_groups["medium"].append(item)
        elif difficulty in ["hard", "very hard"]:
            difficulty_groups["hard"].append(item)
        else:
            logger.warning(f"Unknown difficulty level: {difficulty}")

    # Combine the grouped data
    result = {}

    for group_name, items in difficulty_groups.items():
        if not items:
            # No data for this group
            result[group_name] = {"success_rate": 0.0, "visits": 0}
            continue

        # Calculate weighted average success rate and total visits
        total_visits = sum(item.get("visits", 0) for item in items)

        if total_visits == 0:
            weighted_success_rate = 0.0
        else:
            weighted_success_rate = (
                sum(item.get("success_rate", 0.0) * item.get("visits", 0) for item in items) / total_visits
            )

        result[group_name] = {"success_rate": weighted_success_rate, "visits": total_visits}

    return result


def average_concept_metrics_across_files(file_paths: List[Path]) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Average concept metrics across multiple files.

    Args:
        file_paths: List of paths to concept metrics JSON files

    Returns:
        Dictionary mapping concept names to grouped difficulty metrics
    """
    if not file_paths:
        logger.warning("No file paths provided")
        return {}

    # Load all concept metrics files
    all_concept_data = []
    for file_path in file_paths:
        try:
            concept_data = load_concept_metrics(file_path)
            all_concept_data.append(concept_data)
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            # Continue with other files

    if not all_concept_data:
        logger.error("No valid concept metrics files could be loaded")
        return {}

    # Get all unique concept names across all files
    all_concepts = set()
    for data in all_concept_data:
        all_concepts.update(data.keys())

    logger.info(f"Found {len(all_concepts)} unique concepts across {len(all_concept_data)} files")

    # Process each concept
    averaged_results = {}

    for concept in all_concepts:
        logger.info(f"Processing concept: {concept}")

        # Collect grouped data for this concept from all files
        concept_grouped_data = defaultdict(list)

        for data in all_concept_data:
            if concept in data:
                # Group difficulty levels for this concept in this file
                grouped = group_difficulty_levels(data[concept])

                # Add to collection for averaging
                for difficulty_group, metrics in grouped.items():
                    concept_grouped_data[difficulty_group].append(metrics)
            else:
                # Concept missing in this file - add zeros
                for difficulty_group in ["easy", "medium", "hard"]:
                    concept_grouped_data[difficulty_group].append({"success_rate": 0.0, "visits": 0})

        # Average the grouped data for this concept
        averaged_concept = {}
        for difficulty_group, metrics_list in concept_grouped_data.items():
            avg_success_rate = sum(m["success_rate"] for m in metrics_list) / len(metrics_list)
            avg_visits = sum(m["visits"] for m in metrics_list) / len(metrics_list)

            averaged_concept[difficulty_group] = {"success_rate": avg_success_rate, "visits": avg_visits}

        averaged_results[concept] = averaged_concept

    return averaged_results


def save_averaged_concept_metrics(averaged_results: Dict[str, Dict[str, Dict[str, float]]], output_path: Path) -> None:
    """
    Save averaged concept metrics to a JSON file.

    Args:
        averaged_results: Averaged concept metrics data
        output_path: Path where to save the results
    """
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Structure the output to match the original format
        output_data = {
            "concept_mastery_distribution": averaged_results,
            "metadata": {
                "description": "Averaged concept metrics with grouped difficulty levels",
                "difficulty_groups": {
                    "easy": ["very easy", "easy"],
                    "medium": ["medium"],
                    "hard": ["hard", "very hard"],
                },
            },
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"Saved averaged concept metrics to {output_path}")

    except Exception as e:
        logger.error(f"Failed to save results to {output_path}: {e}")
        raise


def main() -> None:
    """Main function to run the concept metrics averaging script."""
    # Example file paths - modify these for your actual files
    file_paths = [
        Path("experiments/deepseekv3/final-1/whole_tree_analysis/concept_metrics.json"),
        Path("experiments/deepseekv3/final-2/whole_tree_analysis/concept_metrics.json"),
        Path("experiments/deepseekv3/final-3/whole_tree_analysis/concept_metrics.json"),
    ]

    output_path = Path("averaged_concept_metrics.json")

    try:
        # Average the concept metrics
        averaged_results = average_concept_metrics_across_files(file_paths)

        if averaged_results:
            # Save the results
            save_averaged_concept_metrics(averaged_results, output_path)

            # Print summary
            logger.info(f"Successfully averaged {len(averaged_results)} concepts")
            logger.info(f"Concepts processed: {', '.join(sorted(averaged_results.keys()))}")
        else:
            logger.error("No results to save")

    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise


if __name__ == "__main__":
    main()
