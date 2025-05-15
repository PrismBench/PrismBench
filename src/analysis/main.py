from pathlib import Path
from typing import Dict

from .data_loader import DataLoader
from .metrics.basic_metrics import BasicMetricsAnalyzer
from .metrics.concept_metrics import ConceptMetricsAnalyzer
from .metrics.error_metrics import ErrorMetricsAnalyzer
from .metrics.pattern_metrics import PatternMetricsAnalyzer
from .metrics.test_metrics import TestMetricsAnalyzer
from .metrics.tree_metrics import TreeMetricsAnalyzer
from .utils import (
    save_metrics,
    setup_phase_one_output_directories,
    setup_phase_two_output_directories,
    setup_phase_three_output_directories,
    setup_phase_one_and_two_output_directories,
)
from .visualization.basic_viz import BasicVisualizationGenerator
from .visualization.concept_viz import ConceptVisualizationGenerator
from .visualization.error_viz import ErrorVisualizationGenerator
from .visualization.pattern_viz import PatternVisualizationGenerator
from .visualization.test_viz import TestVisualizationGenerator
from .visualization.tree_viz import TreeVisualizationGenerator


class PhaseOneAnalyzer:
    """Main analyzer class that orchestrates the analysis of Phase One MCTS trees"""

    def __init__(self, experiment_path: str):
        """Initialize analyzer with path to experiment directory"""
        self.experiment_path = Path(experiment_path)
        self.directories = setup_phase_one_output_directories(self.experiment_path)

        # Initialize data loader
        self.data_loader = DataLoader(experiment_path, phase="PHASE_ONE")
        self.phase_one_nodes = self.data_loader.get_phase_nodes()

        # Initialize metric analyzers
        self.basic_metrics_analyzer = BasicMetricsAnalyzer(self.phase_one_nodes)
        self.concept_metrics_analyzer = ConceptMetricsAnalyzer(self.phase_one_nodes)
        self.tree_metrics_analyzer = TreeMetricsAnalyzer(self.phase_one_nodes)

        # Initialize visualization generators
        self.basic_viz_generator = BasicVisualizationGenerator(self.directories["viz"])
        self.concept_viz_generator = ConceptVisualizationGenerator(
            self.directories["viz"]
        )
        self.tree_viz_generator = TreeVisualizationGenerator(self.directories["viz"])

    def generate_report(self) -> Dict:
        """
        Generate comprehensive Phase One analysis report.

        This method performs the following steps:
        1. Collects all relevant metrics by analyzing basic performance, concept mastery, and tree growth.
        2. Generates visualizations for each set of metrics.
        3. Saves the collected metrics to JSON files.
        4. Combines all metrics into a single dictionary and returns it.

        Returns:
            Dict: A dictionary containing all collected metrics from the analysis.
        """
        # Collect all metrics
        basic_metrics = self.basic_metrics_analyzer.analyze()
        concept_metrics = self.concept_metrics_analyzer.analyze()
        tree_metrics = self.tree_metrics_analyzer.analyze()

        # Generate visualizations
        self.basic_viz_generator.generate_visualizations(basic_metrics)
        self.concept_viz_generator.generate_visualizations(concept_metrics)
        self.tree_viz_generator.generate_visualizations(tree_metrics)

        # Save metrics to JSON
        save_metrics(basic_metrics, self.directories["output"], "basic_")
        save_metrics(concept_metrics, self.directories["output"], "concept_")
        save_metrics(tree_metrics, self.directories["output"], "tree_")

        # Combine all metrics into a single dictionary
        all_metrics = {
            "basic_metrics": basic_metrics,
            "concept_metrics": concept_metrics,
            "tree_metrics": tree_metrics,
        }

        return all_metrics


class PhaseTwoAnalyzer(PhaseOneAnalyzer):
    """Main analyzer class that orchestrates the analysis of Phase Two MCTS trees"""

    def __init__(self, experiment_path: str):
        """Initialize analyzer with path to experiment directory"""
        super().__init__(experiment_path)
        self.directories = setup_phase_two_output_directories(self.experiment_path)

        # Initialize data loader
        self.data_loader = DataLoader(experiment_path, phase="PHASE_TWO")
        self.phase_two_nodes = self.data_loader.get_phase_nodes()

        # Initialize metric analyzers
        self.basic_metrics_analyzer = BasicMetricsAnalyzer(self.phase_two_nodes)
        self.concept_metrics_analyzer = ConceptMetricsAnalyzer(self.phase_two_nodes)
        self.tree_metrics_analyzer = TreeMetricsAnalyzer(self.phase_two_nodes)

        # Initialize visualization generators
        self.basic_viz_generator = BasicVisualizationGenerator(self.directories["viz"])
        self.concept_viz_generator = ConceptVisualizationGenerator(
            self.directories["viz"]
        )
        self.tree_viz_generator = TreeVisualizationGenerator(self.directories["viz"])


class PhaseOneAndTwoAnalyzer(PhaseOneAnalyzer):
    """Main analyzer class that orchestrates the analysis of Phase One and Two MCTS trees"""

    def __init__(self, experiment_path: str):
        """Initialize analyzer with path to experiment directory"""
        self.experiment_path = Path(experiment_path)
        self.directories = setup_phase_one_and_two_output_directories(
            self.experiment_path
        )

        self.data_loader = DataLoader(experiment_path, phase="PHASE_ONE_AND_TWO")
        self.phase_one_and_two_nodes = self.data_loader.get_phase_nodes()

        # Initialize metric analyzers
        self.basic_metrics_analyzer = BasicMetricsAnalyzer(self.phase_one_and_two_nodes)
        self.concept_metrics_analyzer = ConceptMetricsAnalyzer(
            self.phase_one_and_two_nodes
        )
        self.tree_metrics_analyzer = TreeMetricsAnalyzer(self.phase_one_and_two_nodes)

        # Initialize visualization generators
        self.basic_viz_generator = BasicVisualizationGenerator(self.directories["viz"])
        self.concept_viz_generator = ConceptVisualizationGenerator(
            self.directories["viz"]
        )
        self.tree_viz_generator = TreeVisualizationGenerator(self.directories["viz"])


class PhaseThreeAnalyzer:
    """Main analyzer class that orchestrates the analysis of Phase Three MCTS trees"""

    def __init__(self, experiment_path: str):
        """Initialize analyzer with path to experiment directory"""
        self.experiment_path = Path(experiment_path)
        self.directories = setup_phase_three_output_directories(self.experiment_path)

        # Initialize data loader
        self.data_loader = DataLoader(experiment_path, phase="PHASE_THREE")
        self.phase_three_nodes = self.data_loader.get_phase_nodes()

        # Initialize metric analyzers
        self.pattern_metrics_analyzer = PatternMetricsAnalyzer(self.phase_three_nodes)
        self.test_metrics_analyzer = TestMetricsAnalyzer(self.phase_three_nodes)
        self.error_metrics_analyzer = ErrorMetricsAnalyzer(self.phase_three_nodes)

        # Initialize visualization generators
        self.pattern_viz_generator = PatternVisualizationGenerator(
            self.directories["viz"]
        )
        self.test_viz_generator = TestVisualizationGenerator(self.directories["viz"])
        self.error_viz_generator = ErrorVisualizationGenerator(self.directories["viz"])

    def generate_report(self) -> Dict:
        """Generate comprehensive Phase Three analysis report"""
        solution_pattern_metrics = self.pattern_metrics_analyzer.analyze()
        test_metrics = self.test_metrics_analyzer.analyze()
        error_metrics = self.error_metrics_analyzer.analyze()

        # Generate visualizations
        self.pattern_viz_generator.generate_visualizations(solution_pattern_metrics)
        self.test_viz_generator.generate_visualizations(test_metrics)
        self.error_viz_generator.generate_visualizations(error_metrics)

        # Save metrics to JSON
        save_metrics(solution_pattern_metrics, self.directories["output"], "pattern_")
        save_metrics(test_metrics, self.directories["output"], "test_")
        save_metrics(error_metrics, self.directories["output"], "error_")

        # Combine all metrics into a single dictionary
        all_metrics = {
            "pattern_metrics": solution_pattern_metrics,
            "test_metrics": test_metrics,
            "error_metrics": error_metrics,
        }

        return all_metrics


if __name__ == "__main__":
    phase_one_analyzer = PhaseOneAndTwoAnalyzer(
        "/Users/ahvra/Nexus/Prism/experiments/4o/final-1"
    )
    phase_one_analyzer.generate_report()
