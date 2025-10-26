# Analysis Tools

The Analysis module provides comprehensive tools for processing, visualizing, and interpreting results from PrismBench evaluations.

## Overview

This module transforms raw evaluation data into actionable insights through statistical analysis, visualization generation, and report creation. It supports both real-time monitoring during evaluations and post-hoc analysis of completed runs.

## Key Features

- **Statistical Analysis**: Performance metrics, confidence intervals, significance testing
- **Visualization Generation**: Interactive charts, heatmaps, and tree visualizations  
- **Report Generation**: Automated executive summaries and technical deep-dives
- **Comparative Analysis**: Multi-model benchmarking and performance regression tracking
- **Error Pattern Analysis**: Automated categorization and frequency analysis of failure modes

## Core Components

### Performance Analyzer
Calculates key performance metrics across all evaluation phases:

```python
from src.analysis.performance_analyzer import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()
metrics = analyzer.analyze_phase_results(
    phase1_results, phase2_results, phase3_results
)

print(f"Overall score: {metrics.overall_score}")
print(f"Confidence interval: {metrics.confidence_interval}")
```

### Visualization Engine
Generates interactive and static visualizations:

```python
from src.analysis.visualization import VisualizationEngine

viz = VisualizationEngine()

# Capability heatmap
viz.create_capability_heatmap(
    concept_scores=metrics.concept_performance,
    output_path="results/capability_heatmap.png"
)

# Challenge distribution
viz.create_challenge_distribution(
    challenging_combinations=phase2_results.challenges,
    output_path="results/challenge_distribution.png"
)
```

### Report Generator
Creates comprehensive evaluation reports:

```python
from src.analysis.report_generator import ReportGenerator

report_gen = ReportGenerator()

# Executive summary
summary = report_gen.create_executive_summary(
    evaluation_results=complete_results,
    model_name="gpt-4o-mini"
)

# Technical deep dive
technical_report = report_gen.create_technical_report(
    evaluation_results=complete_results,
    include_raw_data=True
)
```

## Analysis Types

### Phase 1 Analysis: Capability Mapping

**Concept Performance Analysis**
```python
def analyze_concept_performance(phase1_results):
    """Analyze performance across different CS concepts."""
    concept_scores = {}
    
    for result in phase1_results.simulation_results:
        for concept in result.concepts:
            if concept not in concept_scores:
                concept_scores[concept] = []
            concept_scores[concept].append(result.score)
    
    # Calculate statistics
    analysis = {}
    for concept, scores in concept_scores.items():
        analysis[concept] = {
            "mean_score": np.mean(scores),
            "std_dev": np.std(scores),
            "confidence_interval": calculate_ci(scores),
            "sample_size": len(scores)
        }
    
    return analysis
```

**Difficulty Scaling Analysis**
```python
def analyze_difficulty_scaling(phase1_results):
    """Analyze how performance scales with difficulty."""
    difficulty_performance = {}
    
    for result in phase1_results.simulation_results:
        difficulty = result.difficulty_level
        if difficulty not in difficulty_performance:
            difficulty_performance[difficulty] = []
        difficulty_performance[difficulty].append(result.score)
    
    # Fit polynomial to difficulty progression
    difficulties = ["easy", "medium", "hard", "expert"]
    scores = [np.mean(difficulty_performance[d]) for d in difficulties]
    
    return {
        "difficulty_scores": dict(zip(difficulties, scores)),
        "scaling_coefficient": calculate_scaling(scores),
        "difficulty_gaps": calculate_gaps(scores)
    }
```

### Phase 2 Analysis: Challenge Discovery

**Challenge Pattern Analysis**
```python
def analyze_challenge_patterns(phase2_results):
    """Identify patterns in challenging concept combinations."""
    
    # Group challenges by characteristics
    patterns = {
        "by_concept_count": defaultdict(list),
        "by_difficulty": defaultdict(list),
        "by_failure_type": defaultdict(list)
    }
    
    for challenge in phase2_results.challenging_combinations:
        patterns["by_concept_count"][len(challenge.concepts)].append(challenge)
        patterns["by_difficulty"][challenge.difficulty].append(challenge)
        patterns["by_failure_type"][challenge.primary_failure_type].append(challenge)
    
    return {
        "multi_concept_bias": analyze_concept_interaction(patterns["by_concept_count"]),
        "difficulty_distribution": analyze_difficulty_bias(patterns["by_difficulty"]),
        "failure_modes": analyze_failure_patterns(patterns["by_failure_type"])
    }
```

### Phase 3 Analysis: Comprehensive Evaluation

**Solution Pattern Analysis**
```python
def analyze_solution_patterns(phase3_results):
    """Analyze patterns in solution approaches and implementations."""
    
    patterns = {
        "algorithm_preferences": Counter(),
        "data_structure_usage": Counter(),
        "complexity_patterns": [],
        "error_categories": Counter()
    }
    
    for variation in phase3_results.problem_variations:
        # Analyze solution code
        solution_analysis = parse_solution_code(variation.solution_code)
        patterns["algorithm_preferences"].update(solution_analysis.algorithms)
        patterns["data_structure_usage"].update(solution_analysis.data_structures)
        patterns["complexity_patterns"].append(solution_analysis.complexity)
        
        # Analyze errors if any
        if variation.errors:
            error_categories = categorize_errors(variation.errors)
            patterns["error_categories"].update(error_categories)
    
    return patterns
```

## Visualization Types

### Capability Heatmap
Shows performance across concept-difficulty combinations:

```python
def create_capability_heatmap(concept_scores, difficulty_scores):
    """Create capability heatmap visualization."""
    
    # Create matrix
    concepts = list(concept_scores.keys())
    difficulties = ["easy", "medium", "hard", "expert"]
    
    matrix = np.zeros((len(concepts), len(difficulties)))
    for i, concept in enumerate(concepts):
        for j, difficulty in enumerate(difficulties):
            matrix[i][j] = get_score(concept, difficulty)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    # Add labels and colorbar
    ax.set_xticks(range(len(difficulties)))
    ax.set_xticklabels(difficulties)
    ax.set_yticks(range(len(concepts)))
    ax.set_yticklabels(concepts)
    
    plt.colorbar(im, label='Performance Score')
    plt.title('Model Capability Heatmap')
    
    return fig
```

### Challenge Distribution Chart
Visualizes the distribution of challenging concept combinations:

```python
def create_challenge_distribution(challenging_combinations):
    """Create challenge distribution visualization."""
    
    # Group by challenge score ranges
    score_ranges = [(0.0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.0)]
    range_counts = [0] * len(score_ranges)
    
    for challenge in challenging_combinations:
        for i, (low, high) in enumerate(score_ranges):
            if low <= challenge.challenge_score < high:
                range_counts[i] += 1
                break
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    range_labels = [f"{low}-{high}" for low, high in score_ranges]
    bars = ax.bar(range_labels, range_counts, color=['red', 'orange', 'yellow', 'lightgreen'])
    
    ax.set_xlabel('Challenge Score Range')
    ax.set_ylabel('Number of Combinations')
    ax.set_title('Distribution of Challenging Concept Combinations')
    
    return fig
```

### Performance Trends
Shows performance evolution during evaluation:

```python
def create_performance_trends(simulation_history):
    """Create performance trend visualization."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Performance over time
    timestamps = [s.timestamp for s in simulation_history]
    scores = [s.score for s in simulation_history]
    
    ax1.plot(timestamps, scores, alpha=0.6, color='blue')
    ax1.plot(timestamps, smooth(scores), color='red', linewidth=2, label='Trend')
    ax1.set_ylabel('Performance Score')
    ax1.set_title('Performance Over Time')
    ax1.legend()
    
    # Convergence indicators
    convergence_scores = calculate_convergence_scores(simulation_history)
    ax2.plot(timestamps, convergence_scores, color='green')
    ax2.axhline(y=0.01, color='red', linestyle='--', label='Convergence Threshold')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Convergence Score')
    ax2.set_title('Convergence Progress')
    ax2.legend()
    
    return fig
```

## Report Generation

### Executive Summary
High-level overview for stakeholders:

```python
class ExecutiveSummaryTemplate:
    def generate(self, evaluation_results, model_name):
        return {
            "model_name": model_name,
            "evaluation_date": datetime.now(),
            "overall_performance": {
                "score": evaluation_results.overall_score,
                "confidence_interval": evaluation_results.confidence_interval,
                "percentile_rank": self.calculate_percentile(evaluation_results.overall_score)
            },
            "key_strengths": self.identify_strengths(evaluation_results),
            "major_weaknesses": self.identify_weaknesses(evaluation_results),
            "recommendations": self.generate_recommendations(evaluation_results),
            "comparative_analysis": self.compare_to_benchmarks(evaluation_results)
        }
```

### Technical Deep Dive
Detailed analysis for researchers and developers:

```python
class TechnicalReportTemplate:
    def generate(self, evaluation_results, include_raw_data=False):
        report = {
            "methodology": self.describe_methodology(evaluation_results),
            "statistical_analysis": self.perform_statistical_analysis(evaluation_results),
            "phase_breakdown": {
                "phase1": self.analyze_phase1(evaluation_results.phase1_results),
                "phase2": self.analyze_phase2(evaluation_results.phase2_results),
                "phase3": self.analyze_phase3(evaluation_results.phase3_results)
            },
            "error_analysis": self.analyze_errors(evaluation_results),
            "performance_patterns": self.identify_patterns(evaluation_results),
            "appendices": {
                "configuration": evaluation_results.configuration,
                "tree_structure": evaluation_results.final_tree
            }
        }
        
        if include_raw_data:
            report["raw_data"] = evaluation_results.raw_simulation_data
        
        return report
```

## Statistical Analysis

### Confidence Intervals
```python
def calculate_confidence_interval(scores, confidence_level=0.95):
    """Calculate confidence interval for performance scores."""
    n = len(scores)
    mean = np.mean(scores)
    std_err = np.std(scores, ddof=1) / np.sqrt(n)
    
    # t-distribution for small samples
    if n < 30:
        t_val = stats.t.ppf((1 + confidence_level) / 2, n - 1)
        margin_error = t_val * std_err
    else:
        z_val = stats.norm.ppf((1 + confidence_level) / 2)
        margin_error = z_val * std_err
    
    return (mean - margin_error, mean + margin_error)
```

### Significance Testing
```python
def test_performance_difference(model_a_scores, model_b_scores):
    """Test if performance difference between models is significant."""
    
    # Normality test
    _, p_norm_a = stats.shapiro(model_a_scores)
    _, p_norm_b = stats.shapiro(model_b_scores)
    
    if p_norm_a > 0.05 and p_norm_b > 0.05:
        # Use t-test for normal distributions
        statistic, p_value = stats.ttest_ind(model_a_scores, model_b_scores)
        test_type = "t-test"
    else:
        # Use Mann-Whitney U test for non-normal distributions
        statistic, p_value = stats.mannwhitneyu(model_a_scores, model_b_scores)
        test_type = "Mann-Whitney U"
    
    return {
        "test_type": test_type,
        "statistic": statistic,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "effect_size": calculate_effect_size(model_a_scores, model_b_scores)
    }
```

## Usage Examples

### Complete Analysis Pipeline
```python
from src.analysis import AnalysisPipeline

# Initialize pipeline
pipeline = AnalysisPipeline()

# Load evaluation results
results = pipeline.load_results("results/eval_123456/")

# Perform complete analysis
analysis = pipeline.analyze(
    results=results,
    generate_visualizations=True,
    create_reports=True,
    compare_to_baseline="gpt-4o-mini"
)

# Save outputs
pipeline.save_analysis(
    analysis=analysis,
    output_dir="results/eval_123456/analysis/"
)
```

### Custom Analysis
```python
# Custom analysis for specific research questions
def analyze_concept_interaction_effects(results):
    """Analyze how concept combinations affect performance."""
    
    single_concept_scores = []
    multi_concept_scores = []
    
    for result in results.all_simulation_results:
        if len(result.concepts) == 1:
            single_concept_scores.append(result.score)
        else:
            multi_concept_scores.append(result.score)
    
    interaction_effect = np.mean(single_concept_scores) - np.mean(multi_concept_scores)
    significance = test_performance_difference(single_concept_scores, multi_concept_scores)
    
    return {
        "interaction_effect": interaction_effect,
        "significance": significance,
        "single_concept_mean": np.mean(single_concept_scores),
        "multi_concept_mean": np.mean(multi_concept_scores)
    }
```

## Configuration

### Analysis Settings
```yaml
# configs/analysis_config.yml
visualization:
  style: "seaborn"
  figure_size: [12, 8]
  dpi: 300
  color_palette: "viridis"

statistics:
  confidence_level: 0.95
  significance_threshold: 0.05
  minimum_sample_size: 10

reports:
  include_raw_data: false
  generate_appendices: true
  output_format: ["pdf", "html", "json"]
```

For integration details and API reference, see the main [documentation](../../docs/). 