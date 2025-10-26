import asyncio
import json
import os
from collections import defaultdict
from typing import Any, Dict, FrozenSet, List, Tuple

from .interface_client import InterfaceClient


class PatternMetricsAnalyzer:
    """Analyzes solution patterns from nodes"""

    def __init__(self, nodes: List):
        self.nodes = nodes

        self.llm = InterfaceClient(
            base_url=os.getenv("LLM_SERVICE_URL", "http://llm-interface:8000"),
            role="solution_pattern_analyzer",
        )

        # group nodes by concept combination and difficulty
        self.grouped_nodes = self._group_nodes()

        # storage for computed metrics
        self.pattern_distributions = defaultdict(lambda: defaultdict(int))
        self.comparative_metrics = {}

    def _group_nodes(self) -> Dict[Tuple[FrozenSet[str], str], List]:
        """
        Group nodes by their concept combinations and difficulty

        Returns:
            Dict[Tuple[FrozenSet[str], str], List]: Grouped nodes by concept combination and difficulty
        """
        grouped = defaultdict(list)
        for node in self.nodes:
            key = (frozenset(node.concepts), node.difficulty)
            grouped[key].append(node)
        return grouped

    async def analyze(self) -> Dict[str, Any]:
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

        batch_size = 10
        for batch_index, start in enumerate(range(0, len(self.nodes), batch_size), start=1):
            batch_nodes = self.nodes[start : start + batch_size]
            await asyncio.gather(*(self._get_solution_patterns(node) for node in batch_nodes))

        for (concepts, difficulty), nodes in self.grouped_nodes.items():
            concept_key = "-".join(sorted(concepts))

            success_rate = sum(1 for n in nodes if n.run_results and n.run_results[-1].get("success", False)) / len(
                nodes
            )
            avg_attempts = sum(n.run_results[-1].get("attempts", 3) for n in nodes if n.run_results) / len(nodes)

            pattern_counts = defaultdict(int)
            for node in nodes:
                # get solution patterns using LLM if not already present
                try:
                    solution_patterns = node.solution_patterns
                except AttributeError:
                    solution_patterns = None

                if not solution_patterns:
                    continue

                # extract patterns for this node
                node_patterns = self._extract_solution_patterns(solution_patterns)

                # aggregate patterns
                for pattern in node_patterns:
                    if pattern:  # only count non-empty patterns
                        pattern_counts[pattern] += 1
                        metrics["patterns_by_concept_group"][concept_key][pattern] += 1
                        metrics["patterns_by_difficulty"][difficulty][pattern] += 1
                        metrics["total_patterns"][pattern] += 1
                        self.pattern_distributions[concept_key][pattern] += 1

            # store comparative metrics
            self.comparative_metrics[f"{concept_key}-{difficulty}"] = {
                "success_rate": success_rate,
                "avg_attempts": avg_attempts,
                "patterns": dict(pattern_counts),
                "pattern_distribution": {
                    "algorithmic_patterns": sum(1 for p in pattern_counts if "algorithm" in p.lower()),
                    "data_structure_patterns": sum(1 for p in pattern_counts if "data structure" in p.lower()),
                    "optimization_patterns": sum(1 for p in pattern_counts if "optimization" in p.lower()),
                    "implementation_patterns": sum(1 for p in pattern_counts if "implementation" in p.lower()),
                },
            }

        return {
            **metrics,
            "comparative_analysis": self.comparative_metrics,
            "pattern_distributions": dict(self.pattern_distributions),
        }

    async def _get_solution_patterns(self, node) -> None:
        """
        Get solution patterns analysis from LLM

        Args:
            node: Node to analyze

        Returns:
            None
        """
        try:
            solution_patterns = node.solution_patterns
        except AttributeError:
            solution_patterns = None

        # if already computed, skip re-computation
        if solution_patterns:
            return

        if not node.run_results:
            node.solution_patterns = {}
            return

        latest_attempt = node.run_results[-1]
        data_trail = latest_attempt.get("data_trail", [])
        if not data_trail:
            node.solution_patterns = {}
            return

        solution_code = data_trail[-1].get("solution_code", "")
        if not solution_code:
            node.solution_patterns = {}
            return

        response = await self.llm.interact(
            solution_code=solution_code,
            problem_description=node.challenge_description,
        )

        await self.llm.close()

        try:
            pattern_json = json.loads(response)
        except json.JSONDecodeError:
            pattern_json = {}
        except TypeError:
            pattern_json = {}

        node.solution_patterns = pattern_json

    def _extract_solution_patterns(self, patterns: Dict) -> List[str]:
        """
        Extract patterns from solution pattern analysis

        Args:
            patterns: Solution pattern analysis

        Returns:
            List of patterns
        """
        extracted_patterns = []

        if "algorithm_patterns" in patterns:
            extracted_patterns.append(patterns["algorithm_patterns"].get("main_strategy", ""))
            extracted_patterns.extend(patterns["algorithm_patterns"].get("optimization_techniques", []))

        if "data_structures" in patterns:
            extracted_patterns.extend(patterns["data_structures"].get("primary", []))

        return [p for p in extracted_patterns if p]
