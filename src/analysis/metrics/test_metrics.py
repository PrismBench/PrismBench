import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Tuple

import yaml


class TestMetricsAnalyzer:
    """Analyzes test validation metrics from nodes"""

    def __init__(self, nodes: List):
        """
        Initialize analyzer with nodes

        Args:
            nodes: List of nodes to analyze
        """
        self.nodes = nodes
        self.validation_categories = self._load_validation_categories()

        # Group nodes by concept combination and difficulty
        self.grouped_nodes = self._group_nodes()

        # Storage for computed metrics
        self.validation_distributions = defaultdict(lambda: defaultdict(int))
        self.comparative_metrics = {}

    def _group_nodes(self) -> Dict[Tuple[FrozenSet[str], str], List]:
        """Group nodes by their concept combinations and difficulty"""
        grouped = defaultdict(list)
        for node in self.nodes:
            key = (frozenset(node.concepts), node.difficulty)
            grouped[key].append(node)
        return grouped

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze test validation issues across all nodes.

        Returns:
            Dict containing various test validation metrics and analyses:
            - validation_issues_by_concept_group: Issues grouped by concept combinations
            - validation_issues_by_difficulty: Issues grouped by difficulty
            - total_validation_issues: Total count of each issue type
            - comparative_analysis: Detailed comparative analysis of validation issues
            - validation_distributions: Validation issue distribution across concept combinations
        """
        metrics = {
            "validation_issues_by_concept_group": defaultdict(lambda: defaultdict(int)),
            "validation_issues_by_difficulty": defaultdict(lambda: defaultdict(int)),
            "total_validation_issues": defaultdict(int),
        }

        for (concepts, difficulty), nodes in self.grouped_nodes.items():
            concept_key = "-".join(sorted(concepts))

            # Calculate success metrics
            success_rate = sum(1 for n in nodes if n.run_results and n.run_results[-1].get("success", False)) / len(
                nodes
            )
            avg_attempts = sum(n.run_results[-1].get("attempts", 3) for n in nodes if n.run_results) / len(nodes)

            validation_issues = defaultdict(int)
            for node in nodes:
                test_validation = node.run_results[-1].get("test_validation", "")
                if not test_validation:
                    continue

                # Analyze validation issues for this node
                node_issues = self._analyze_test_validation_issues(test_validation)

                # Aggregate issues
                for issue_type, count in node_issues.items():
                    validation_issues[issue_type] += count
                    metrics["validation_issues_by_concept_group"][concept_key][issue_type] += count
                    metrics["validation_issues_by_difficulty"][difficulty][issue_type] += count
                    metrics["total_validation_issues"][issue_type] += count
                    self.validation_distributions[concept_key][issue_type] += count

            # Store comparative metrics
            self.comparative_metrics[f"{concept_key}-{difficulty}"] = {
                "success_rate": success_rate,
                "avg_attempts": avg_attempts,
                "validation_issues": dict(validation_issues),
                "validation_distribution": {
                    "missing_scenarios": sum(1 for i in validation_issues if "missing" in i),
                    "incorrect_assertions": sum(1 for i in validation_issues if "incorrect" in i),
                    "coverage_gaps": sum(1 for i in validation_issues if "coverage" in i),
                    "edge_cases": sum(1 for i in validation_issues if "edge" in i),
                },
            }

        return {
            **metrics,
            "comparative_analysis": self.comparative_metrics,
            "validation_distributions": dict(self.validation_distributions),
        }

    def _analyze_test_validation_issues(self, test_validation: str) -> Dict[str, int]:
        """Analyze test validation issues with enhanced detail capture."""
        validation_issues = defaultdict(int)

        # Extract and analyze each section
        sections = {
            "missing": r"Missing Test Scenarios[:\n]+(.*?)(?=\n\d+\.|$)",
            "incorrect": r"Incorrect Assertions[:\n]+(.*?)(?=\n\d+\.|$)",
            "coverage": r"Suggestions for Improving Test Coverage[:\n]+(.*?)(?=\n\d+\.|$)",
            "edge": r"Analysis of Edge Cases[:\n]+(.*?)(?=\n\d+\.|$)",
        }

        section_to_category = {
            "missing": "missing_test_scenarios",
            "incorrect": "incorrect_assertions",
            "coverage": "coverage_gaps",
            "edge": "edge_case_analysis",
        }

        for section_name, pattern in sections.items():
            if section_match := re.search(pattern, test_validation, re.DOTALL):
                section_content = section_match.group(1)
                category = section_to_category[section_name]

                if category in self.validation_categories:
                    for subcat, subpattern in self.validation_categories[category].items():
                        matches = re.finditer(subpattern, section_content, re.IGNORECASE)
                        validation_issues[f"{section_name}_{subcat}"] += sum(1 for _ in matches)

        # Capture specific suggestions count
        suggestions = re.findall(r"-\s*(.*?)(?=(?:-|\Z))", test_validation, re.DOTALL)
        validation_issues["total_suggestions"] = len(suggestions)

        return dict(validation_issues)

    def _load_validation_categories(self) -> Dict:
        """Load validation categories from YAML file"""
        yaml_path = Path(__file__).parent.parent / "configs" / "validation_categories.yml"
        try:
            with open(yaml_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
