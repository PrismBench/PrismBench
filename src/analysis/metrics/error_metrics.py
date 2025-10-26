import asyncio
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Tuple

import spacy
import yaml

from .interface_client import InterfaceClient


class ErrorMetricsAnalyzer:
    """Analyzes error patterns from nodes"""

    def __init__(self, nodes: List):
        self.nodes = nodes
        self.error_type_keywords = self._load_error_types()
        self.nlp = spacy.load("en_core_web_sm")

        self.llm = InterfaceClient(
            base_url=os.getenv("LLM_SERVICE_URL", "http://llm-interface:8000"),
            role="test_error_analyzer",
        )

        # Group nodes by concept combination and difficulty
        self.grouped_nodes = self._group_nodes()

        # Storage for computed metrics
        self.error_distributions = defaultdict(lambda: defaultdict(int))
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
        """Analyze error patterns across all nodes."""
        metrics = {
            "error_patterns_by_concept_group": defaultdict(lambda: defaultdict(int)),
            "error_patterns_by_difficulty": defaultdict(lambda: defaultdict(int)),
            "total_error_patterns": defaultdict(int),
        }
        batch_size = 10
        for batch_index, start in enumerate(range(0, len(self.nodes), batch_size), start=1):
            batch_nodes = self.nodes[start : start + batch_size]
            await asyncio.gather(*(self._get_error_analysis(node) for node in batch_nodes))

        for (concepts, difficulty), nodes in self.grouped_nodes.items():
            concept_key = "-".join(sorted(concepts))

            success_rate = sum(1 for n in nodes if n.run_results and n.run_results[-1].get("success", False)) / len(
                nodes
            )
            avg_attempts = sum(n.run_results[-1].get("attempts", 3) for n in nodes if n.run_results) / len(nodes)

            error_patterns = defaultdict(int)
            for node in nodes:
                try:
                    error_analysis = node.error_analysis
                except AttributeError:
                    error_analysis = None

                if not error_analysis:
                    continue

                node_patterns = self._analyze_error_patterns(error_analysis)

                for error_type, count in node_patterns.items():
                    error_patterns[error_type] += count
                    metrics["error_patterns_by_concept_group"][concept_key][error_type] += count
                    metrics["error_patterns_by_difficulty"][difficulty][error_type] += count
                    metrics["total_error_patterns"][error_type] += count
                    self.error_distributions[concept_key][error_type] += count

            self.comparative_metrics[f"{concept_key}-{difficulty}"] = {
                "success_rate": success_rate,
                "avg_attempts": avg_attempts,
                "error_patterns": dict(error_patterns),
                "error_distribution": {
                    "logic_errors": sum(1 for p in error_patterns if "logic" in p),
                    "implementation_errors": sum(1 for p in error_patterns if "implementation" in p),
                    "edge_case_errors": sum(1 for p in error_patterns if "edge" in p),
                    "test_setup_errors": sum(1 for p in error_patterns if "setup" in p),
                },
            }

        return {
            **metrics,
            "comparative_analysis": self.comparative_metrics,
            "error_distributions": dict(self.error_distributions),
        }

    async def _get_error_analysis(self, node) -> None:
        """Get error analysis from LLM"""
        try:
            error_analysis = node.error_analysis
        except AttributeError:
            error_analysis = None

        if error_analysis:
            return

        if not node.run_results:
            node.error_analysis = {}
            return

        latest_attempt = node.run_results[-1]
        data_trail = latest_attempt.get("data_trail", [])
        if not data_trail:
            node.error_analysis = {}
            return

        output = data_trail[-1].get("output", "")
        solution_code = data_trail[-1].get("solution_code", "")
        if not output:
            node.error_analysis = {}
            return

        response = await self.llm.interact(
            test_output=output,
            code_under_test=solution_code,
        )

        await self.llm.close()

        try:
            error_analysis_json = response
        except Exception as e:
            print(e)
            error_analysis_json = {}

        node.error_analysis = error_analysis_json

    def _analyze_error_patterns(self, output: str) -> Dict[str, int]:
        """Analyze error patterns in test output using NLP and lemmatization"""
        error_patterns = defaultdict(int)

        # Remove error analysis tags if present
        output = re.sub(r"</?error_analysis>", "", output, flags=re.IGNORECASE)

        # Define patterns for section extraction
        section_patterns = {
            "test_failures": (
                r"Test Failures:(.*?)(?="
                r"(Test Error:|Root Causes:|Suggested Areas to Investigate:|What Went Wrong:|$))"
            ),
            "root_causes": (
                r"Root Causes:(.*?)(?="
                r"(Test Error:|Suggested Areas to Investigate:|What Went Wrong:|$))"
            ),
            "suggested_areas": (
                r"Suggested Areas to Investigate:(.*?)(?="
                r"(Test Error:|What Went Wrong:|$))"
            ),
        }

        # Pre-process keywords using lemmatization
        lemmatized_keywords = {}
        for error_type, keywords in self.error_type_keywords.items():
            lemmas = set()
            for keyword in keywords:
                doc = self.nlp(keyword.lower())
                lemmas.update([token.lemma_ for token in doc if token.lemma_ != "-PRON-"])
            lemmatized_keywords[error_type] = lemmas

        # Extract and analyze each section
        for section_name, pattern in section_patterns.items():
            if match := re.search(pattern, output, re.DOTALL | re.IGNORECASE):
                text = match.group(1).strip()
                if not text:
                    continue

                # Determine section prefix for error pattern keys
                section_prefix = ""
                if section_name == "root_causes":
                    section_prefix = "root"
                elif section_name == "suggested_areas":
                    section_prefix = "fix"

                # Analyze text using spaCy and lemmatization
                doc = self.nlp(text.lower())
                for sent in doc.sents:
                    sent_lemmas = {token.lemma_ for token in sent}
                    for error_type, keywords in lemmatized_keywords.items():
                        if sent_lemmas & keywords:  # Check for intersection
                            error_key = f"{section_prefix}_{error_type}" if section_prefix else error_type
                            error_patterns[error_key] += 1

        return dict(error_patterns)

    def _load_error_types(self) -> Dict:
        """Load error type keywords from YAML file"""
        yaml_path = Path(__file__).parent.parent / "configs" / "error_types.yml"
        try:
            with open(yaml_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
