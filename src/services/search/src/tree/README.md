# Tree Structure Framework

> A hierarchical data structure for managing challenge nodes in Monte Carlo Tree Search algorithms with support for multi-phase evaluation, performance tracking, and visualization.

The Tree Structure Framework provides a foundation for building and managing complex tree structures where nodes represent challenges with varying concepts and difficulty levels. It's designed to integrate seamlessly with search algorithms while maintaining flexibility for diverse problem domains.

## Quick Start

```python
# 1. Import and setup
from src.tree import Tree, ChallengeNode

# 2. Initialize tree
tree = Tree(
    concepts=["loops", "functions", "arrays"],
    difficulties=["very easy", "easy", "medium", "hard", "very hard"]
)
tree.initialize_tree()

# 3. Add custom nodes
parent_node = tree.nodes[0]
new_node = tree.add_node([parent_node], difficulty="medium")

# 4. Visualize and save
tree.visualize_tree("my_tree")
tree.save_tree("my_tree_state")
```

## Table of Contents

- [Tree Structure Philosophy](#tree-structure-philosophy)
- [Getting Started](#getting-started)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [Configuration and Initialization](#configuration-and-initialization)
- [API Documentation](#api-documentation)
- [Advanced Usage](#advanced-usage)
- [Performance and Scoring](#performance-and-scoring)
- [Visualization and Persistence](#visualization-and-persistence)

## Tree Structure Philosophy

The Tree Structure Framework is built on several key principles:

- **Hierarchical Organization**: Nodes maintain parent-child relationships with automatic depth tracking and ancestor resolution.
- **Multi-Phase Support**: Nodes can belong to different phases, enabling complex multi-objective search strategies.
- **Performance Tracking**: Built-in metrics for visits, successes, failures, and custom scoring systems.
- **Flexible Expansion**: Dynamic node creation based on concept combinations and difficulty progression.
- **Visualization Ready**: Integrated visualization capabilities with phase-specific styling and performance indicators.
- **Persistence**: Save and load tree states for experiment continuity and analysis.

## Getting Started

### Installation

The framework is part of the PrismBench project:

```bash
pip install -r requirements.txt
# For visualization support
brew install graphviz  # macOS
# or
sudo apt-get install graphviz  # Ubuntu/Debian
```

### Basic Usage

#### 1. Create a Simple Tree

```python
from src.tree import Tree

# Initialize with your domain concepts
tree = Tree(
    concepts=["variables", "functions", "loops", "conditionals"],
    difficulties=["very easy", "easy", "medium", "hard", "very hard"]
)

# Create initial tree structure
tree.initialize_tree()
print(f"Created tree with {len(tree.nodes)} nodes")
```

#### 2. Work with Individual Nodes

```python
from src.tree import ChallengeNode

# Create a custom node
node = ChallengeNode(
    difficulty="medium",
    concepts=["loops", "arrays"],
    challenge_description="Iterate through an array and process elements",
    depth=2,
    phase=1
)

# Update node performance
node.update_node_score(learning_rate=0.1, reward=0.8)
print(f"Node value: {node.value:.3f}, Visits: {node.visits}")
```

#### 3. Tree Operations

```python
# Add nodes based on existing nodes
parent_nodes = tree.nodes[:2]  # Select first two nodes
new_node = tree.add_node(
    parent_nodes=parent_nodes,
    concepts=["advanced_algorithms"],
    difficulty="hard",
    phase=2
)

# Calculate performance scores
results = {
    "tests_passed_num": 8,
    "tests_failed_num": 2,
    "tests_errored_num": 0,
    "attempt_num": 1,
    "fixed_by_problem_fixer": False
}
score = tree.calculate_performance_score(results)
print(f"Performance score: {score:.3f}")
```

## Architecture

### Directory Structure

```
src/tree/
├── __init__.py           # Module exports
├── tree.py              # Main Tree class implementation
├── node.py              # ChallengeNode class implementation
└── README.md            # This documentation
```

## Core Components

### Tree Class

The `Tree` class serves as the main container and manager for the entire tree structure:

**Key Responsibilities**:
- **Node Management**: Creation, organization, and relationship tracking
- **Initialization**: Automated tree structure creation from concepts
- **Difficulty Assignment**: Intelligent difficulty progression based on parent nodes
- **Performance Calculation**: Standardized scoring across different evaluation metrics
- **Visualization**: Rich graphical representations with phase-specific styling
- **Persistence**: Save/load functionality for experiment continuity

### ChallengeNode Class

The `ChallengeNode` class represents individual challenges within the tree:

**Key Properties**:
- **Identity**: Unique ID and hierarchical position
- **Challenge Data**: Concepts, difficulty, description, and implementation details
- **Performance Metrics**: Visits, successes, failures, and computed values
- **Relationships**: Parent and children node references
- **Phase Information**: Multi-phase evaluation support

## Configuration and Initialization

### Tree Initialization

```python
# Basic initialization
tree = Tree(
    concepts=["concept1", "concept2", "concept3"],
    difficulties=["easy", "medium", "hard"]
)

# Initialize tree structure
tree.initialize_tree()
```

**Initialization Process**:
1. **Root Node Creation**: One node per concept at the easiest difficulty
2. **Combination Generation**: All pairwise combinations of root nodes
3. **Automatic Relationships**: Parent-child relationships and depth assignment

### Custom Node Creation

```python
# Create node with specific parameters
node = ChallengeNode(
    difficulty="hard",
    concepts=["algorithms", "data_structures"],
    challenge_description="Implement a balanced binary search tree",
    parents=[parent1, parent2],
    depth=3,
    phase=2
)

# Add to tree with automatic relationship management
tree.add_node([parent_node], concepts=["new_concept"], difficulty="medium")
```

## API Documentation

### Tree Class

#### Constructor

```python
Tree(concepts: list, difficulties: list) -> None
```

**Parameters**:
- `concepts` (list): List of domain concepts for tree initialization
- `difficulties` (list): List of difficulty levels in ascending order

#### Core Methods

##### Node Management

```python
def initialize_tree() -> None:
    """Initialize tree with root nodes and concept combinations."""

def add_node(
    parent_nodes: Union[ChallengeNode, list[ChallengeNode]], 
    **kwargs
) -> ChallengeNode:
    """Add new node to tree with specified or computed properties."""

def assign_difficulty(parent_nodes: list[ChallengeNode]) -> str:
    """Assign difficulty based on parent node characteristics."""
```

##### Visualization and Export

```python
def visualize_tree(file_name: str = "tree") -> None:
    """Generate visual representation with phase-specific styling."""

def save_tree(file_name: str = "tree") -> None:
    """Save tree state to pickle file."""

def load_tree(file_name: str = "tree") -> None:
    """Load tree state from pickle file."""

def to_dict() -> dict:
    """Serialize tree to dictionary for JSON export."""
```

### ChallengeNode Class

#### Constructor

```python
ChallengeNode(
    difficulty: str,
    concepts: list[str],
    challenge_description: str,
    parents: Union[ChallengeNode, list[ChallengeNode], None] = None,
    depth: int = 0,
    phase: int = 1
) -> None
```

#### Core Methods

##### Performance Tracking

```python
def update_node_score(learning_rate: float, reward: float) -> None:
    """Update node value using temporal difference learning."""

def ucb1(exploration_weight: float = 1.414) -> float:
    """Calculate Upper Confidence Bound for MCTS selection."""
```

##### Relationship Management

```python
def get_node_ancestors_ids() -> list[str]:
    """Return list of all ancestor node IDs."""

def to_dict() -> dict:
    """Serialize node to dictionary with relationship references."""
```

#### Node Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | str | Unique identifier (UUID4) |
| `difficulty` | str | Difficulty level |
| `concepts` | list[str] | Associated concepts |
| `challenge_description` | str | Human-readable description |
| `parents` | list[ChallengeNode] | Parent node references |
| `children` | list[ChallengeNode] | Child node references |
| `depth` | int | Distance from root nodes |
| `phase` | int | Evaluation phase (1, 2, or 3) |
| `visits` | int | Number of evaluations |
| `value` | float | Current node value/score |
| `run_results` | list | Historical evaluation results |

## Advanced Usage

### Custom Difficulty Assignment

```python
class CustomTree(Tree):
    def assign_difficulty(self, parent_nodes: list[ChallengeNode]) -> str:
        """Custom difficulty assignment logic."""
        # Implement domain-specific difficulty progression
        average_performance = sum(node.value for node in parent_nodes) / len(parent_nodes)
        
        if average_performance > 0.8:
            # High performance -> increase difficulty significantly
            max_difficulty_idx = max(self.difficulties.index(node.difficulty) for node in parent_nodes)
            return self.difficulties[min(max_difficulty_idx + 2, len(self.difficulties) - 1)]
        else:
            # Standard progression
            return super().assign_difficulty(parent_nodes)
```

### Multi-Phase Tree Management

```python
# Separate nodes by phase
phase_1_nodes = [node for node in tree.nodes if node.phase == 1]
phase_2_nodes = [node for node in tree.nodes if node.phase == 2]
phase_3_nodes = [node for node in tree.nodes if node.phase == 3]

# Create phase-specific subtrees
def create_phase_tree(nodes: list[ChallengeNode]) -> Tree:
    """Create a tree containing only specified nodes."""
    subtree = Tree(concepts=[], difficulties=[])
    subtree.nodes = nodes
    return subtree

phase_2_tree = create_phase_tree(phase_2_nodes)
phase_2_tree.visualize_tree("phase_2_only")
```


## Performance and Scoring


### UCB1 Calculation

For MCTS integration, nodes support Upper Confidence Bound calculation:

```python
# UCB1 for node selection in MCTS
ucb_value = node.ucb1(exploration_weight=1.414)

# Custom exploration weights for different strategies
conservative_ucb = node.ucb1(exploration_weight=0.7)  # Less exploration
aggressive_ucb = node.ucb1(exploration_weight=2.0)    # More exploration
```

## Visualization and Persistence

### Visualization Features

The tree visualization system provides rich, informative graphics:

**Phase-Specific Styling**:
- **Phase 1**: Light yellow background, dark blue borders
- **Phase 2**: Light green background, dark green borders  
- **Phase 3**: Light blue background, dark blue borders

**Performance Indicators**:
- **Edge Colors**: Green (improvement), Red (decline), Gray (no change)
- **Node Information**: Concepts, difficulty, score, visits, challenge description
- **Legend**: Automatic legend generation for phase identification

```python
# Basic visualization
tree.visualize_tree("experiment_results")

# Multiple format export
tree.visualize_tree("detailed_analysis")  # Creates SVG and PDF
```

### Persistence Options

```python
# Save/load tree state
tree.save_tree("checkpoint_1")
tree.load_tree("checkpoint_1")

# JSON export for analysis
tree_data = tree.to_dict()
with open("tree_export.json", "w") as f:
    json.dump(tree_data, f, indent=2)

# Individual node export
node_data = node.to_dict()
```

### Export Data Structure

```json
{
  "nodes": [
    {
      "id": "uuid-string",
      "difficulty": "medium",
      "concepts": ["loops", "arrays"],
      "challenge_description": "Process array elements",
      "depth": 2,
      "phase": 1,
      "visits": 15,
      "value": 0.742,
      "children": ["child-id-1", "child-id-2"],
      "parents": ["parent-id-1"]
    }
  ],
  "concepts": ["loops", "arrays", "functions"],
  "difficulties": ["easy", "medium", "hard"]
}
```

For more information about integrating with MCTS algorithms, see the [MCTS Documentation](../mcts/README.md).
