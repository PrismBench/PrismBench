import asyncio
from pathlib import Path
from typing import Dict

from .data_loader import DataLoader
from .metrics.basic_metrics import BasicMetricsAnalyzer
from .metrics.concept_metrics import ConceptMetricsAnalyzer
from .metrics.error_metrics import ErrorMetricsAnalyzer
from .metrics.pattern_metrics import PatternMetricsAnalyzer
from .metrics.test_metrics import TestMetricsAnalyzer
from .metrics.tree_metrics import TreeMetricsAnalyzer
from .utils import save_metrics, setup_output_directories


class Analyzer:
    """Main analyzer class that orchestrates the analysis of MCTS trees"""

    def __init__(self, experiment_path: str):
        """Initialize analyzer with path to experiment directory"""
        self.experiment_path = Path(experiment_path)
        self.directories = setup_output_directories(self.experiment_path)

        # Initialize data loader
        self.data_loader = DataLoader(experiment_path)
        self.nodes = self.data_loader.get_phase_nodes()

        # Initialize metric analyzers
        self.basic_metrics_analyzer = BasicMetricsAnalyzer(self.nodes)
        self.concept_metrics_analyzer = ConceptMetricsAnalyzer(self.nodes)
        self.tree_metrics_analyzer = TreeMetricsAnalyzer(self.nodes)

        self.pattern_metrics_analyzer = PatternMetricsAnalyzer(self.nodes)
        self.test_metrics_analyzer = TestMetricsAnalyzer(self.nodes)
        self.error_metrics_analyzer = ErrorMetricsAnalyzer(self.nodes)

    def generate_report(self, diagnostic: bool = False) -> Dict:
        """
        Generate comprehensive Phase One analysis report.

        This method performs the following steps:
        1. Collects all relevant metrics by analyzing basic performance, concept mastery, and tree growth.
        2. Collects error patterns, solution patterns, and test metrics.
        3. Saves the collected metrics to JSON files.

        Returns:
            Dict: A dictionary containing all collected metrics from the analysis.
        """
        # Collect all metrics
        basic_metrics = self.basic_metrics_analyzer.analyze()
        save_metrics(basic_metrics, self.directories["output"], "basic_")

        concept_metrics = self.concept_metrics_analyzer.analyze()
        save_metrics(concept_metrics, self.directories["output"], "concept_")

        tree_metrics = self.tree_metrics_analyzer.analyze()
        save_metrics(tree_metrics, self.directories["output"], "tree_")

        if diagnostic:
            solution_pattern_metrics = asyncio.run(self.pattern_metrics_analyzer.analyze())
            save_metrics(solution_pattern_metrics, self.directories["output"], "pattern_")
            error_metrics = asyncio.run(self.error_metrics_analyzer.analyze())
            save_metrics(error_metrics, self.directories["output"], "error_")


if __name__ == "__main__":
    phase_one_analyzer = Analyzer("/PrismBench/experiments/gpt-oss-20b/final-3")
    phase_one_analyzer.generate_report(diagnostic=True)
