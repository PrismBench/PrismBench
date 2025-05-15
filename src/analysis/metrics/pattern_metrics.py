import json
from collections import defaultdict
from typing import Any, Dict, FrozenSet, List, Tuple

import utils
from llm_interface import LLMInterface


class PatternMetricsAnalyzer:
    """Analyzes solution patterns from nodes"""

    def __init__(self, nodes: List, llm_config_path: str = "agent_config_v7.yml"):
        """
        Initialize analyzer with nodes

        Args:
            nodes: List of nodes to analyze
            llm_config_path: Path to LLM configuration file
        """
        self.nodes = nodes
        self.llm = LLMInterface(llm_config_path)
        self.llm.set_role("solution_pattern_analyzer")

        # Group nodes by concept combination and difficulty
        self.grouped_nodes = self._group_nodes()

        # Storage for computed metrics
        self.pattern_distributions = defaultdict(lambda: defaultdict(int))
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
        Analyze solution patterns across all nodes.

        Returns:
            Dict containing various pattern metrics and analyses:
            - patterns_by_concept_group: Solution patterns grouped by concept combinations
            - patterns_by_difficulty: Solution patterns grouped by difficulty
            - total_patterns: Total count of each pattern type
            - comparative_analysis: Detailed comparative analysis of patterns
            - pattern_distributions: Pattern distribution across concept combinations
        """
        metrics = {
            "patterns_by_concept_group": defaultdict(lambda: defaultdict(int)),
            "patterns_by_difficulty": defaultdict(lambda: defaultdict(int)),
            "total_patterns": defaultdict(int),
        }

        for (concepts, difficulty), nodes in self.grouped_nodes.items():
            concept_key = "-".join(sorted(concepts))

            # Calculate success metrics
            success_rate = sum(
                1
                for n in nodes
                if n.run_results and n.run_results[-1].get("success", False)
            ) / len(nodes)
            avg_attempts = sum(
                n.run_results[-1].get("attempts", 3) for n in nodes
            ) / len(nodes)

            pattern_counts = defaultdict(int)
            for node in nodes:
                # Get solution patterns using LLM if not already present
                try:
                    solution_patterns = node.solution_patterns
                except AttributeError:
                    solution_patterns = None

                if not solution_patterns and node.run_results:
                    latest_attempt = node.run_results[-1]
                    solution_code = latest_attempt.get("solution_code", "")
                    if solution_code:
                        solution_patterns = self._get_solution_patterns(
                            solution_code, node.challenge_description
                        )
                        node.solution_patterns = solution_patterns

                if not solution_patterns:
                    continue

                # Extract patterns for this node
                node_patterns = self._extract_solution_patterns(solution_patterns)

                # Aggregate patterns
                for pattern in node_patterns:
                    if pattern:  # Only count non-empty patterns
                        pattern_counts[pattern] += 1
                        metrics["patterns_by_concept_group"][concept_key][pattern] += 1
                        metrics["patterns_by_difficulty"][difficulty][pattern] += 1
                        metrics["total_patterns"][pattern] += 1
                        self.pattern_distributions[concept_key][pattern] += 1

            # Store comparative metrics
            self.comparative_metrics[f"{concept_key}-{difficulty}"] = {
                "success_rate": success_rate,
                "avg_attempts": avg_attempts,
                "patterns": dict(pattern_counts),
                "pattern_distribution": {
                    "algorithmic_patterns": sum(
                        1 for p in pattern_counts if "algorithm" in p.lower()
                    ),
                    "data_structure_patterns": sum(
                        1 for p in pattern_counts if "data structure" in p.lower()
                    ),
                    "optimization_patterns": sum(
                        1 for p in pattern_counts if "optimization" in p.lower()
                    ),
                    "implementation_patterns": sum(
                        1 for p in pattern_counts if "implementation" in p.lower()
                    ),
                },
            }

        return {
            **metrics,
            "comparative_analysis": self.comparative_metrics,
            "pattern_distributions": dict(self.pattern_distributions),
        }

    def _get_solution_patterns(
        self, solution_code: str, problem_description: str
    ) -> Dict:
        """Get solution patterns analysis from LLM"""
        if not solution_code:
            return {}

        response = self.llm.interact(
            solution_code=solution_code,
            problem_description=problem_description,
        )
        self.llm.clear_memory()

        # Extract JSON from response
        pattern_json = utils.extract_content_from_text(
            response, "<pattern_analysis>", "</pattern_analysis>"
        )

        try:
            return json.loads(pattern_json)
        except json.JSONDecodeError:
            return {}
        except TypeError:
            return {}

    def _extract_solution_patterns(self, patterns: Dict) -> List[str]:
        """Extract patterns from solution pattern analysis"""
        extracted_patterns = []

        if "algorithm_patterns" in patterns:
            extracted_patterns.append(
                patterns["algorithm_patterns"].get("main_strategy", "")
            )
            extracted_patterns.extend(
                patterns["algorithm_patterns"].get("optimization_techniques", [])
            )

        if "data_structures" in patterns:
            extracted_patterns.extend(patterns["data_structures"].get("primary", []))

        return [p for p in extracted_patterns if p]
