# Search Service

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MCTS](https://img.shields.io/badge/Algorithm-MCTS-orange.svg)](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)

> Multi-phase Monte Carlo Tree Search service for systematic LLM capability evaluation

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [MCTS Implementation](#mcts-implementation)
- [Configuration](#configuration)
- [Development](#development)
- [Advanced Usage](#advanced-usage)

## Overview

The Search Service provides APIs for:

- **Session Management**: Creating and managing search sessions with tree structures
- **Task Orchestration**: Running MCTS (Monte Carlo Tree Search) phases asynchronously
- **Tree Operations**: Retrieving and visualizing search tree data

### Core Functionality

This service implements a three-phase MCTS algorithm:

1. **Phase 1**: Initial capability mapping across CS concepts
2. **Phase 2**: Challenge discovery to identify difficult areas
3. **Phase 3**: Comprehensive evaluation of challenging combinations

## Quick Start

### Prerequisites

- Python 3.12+
- FastAPI
- Pydantic v2
- AsyncIO support

### Installation

```bash
# Install dependencies
uv pip install -e .

# Configure the service
cp configs/params.yml.example configs/params.yml
# Edit params.yml with your settings

# Run the service
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

### Verify Installation

```bash
curl http://localhost:8002/health
```

### Basic Configuration

The service loads configuration from `configs/params.yml`:

```yaml
tree_configs:
  concepts: ["loops", "functions", "classes"]
  difficulties: ["very easy", "easy", "medium", "hard", "veryhard"]

phase1:
  phase_params:
    max_iterations: 100
    convergence_checks: 5
  search_params:
    exploration_probability: 0.2
  scoring_params:
    penalty_per_failure: -0.1
```

## Architecture

### Project Structure

```
src/
├── main.py                   # Application entry point
├── core/                     # Core business rules and configuration
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # Dependency injection
│   └── exceptions.py        # Custom exception handling
├── api/                      # API layer (controllers)
│   └── v1/
│       ├── router.py        # Main API router
│       └── endpoints/       # Endpoint implementations
├── services/                 # Business logic layer
│   ├── session_service.py   # Session management
│   ├── task_service.py      # Task orchestration
│   └── mcts_service.py      # MCTS execution
├── repositories/             # Data access layer
│   ├── session_repository.py
│   └── task_repository.py
├── models/                   # Data models
│   ├── domain.py            # Domain models
│   ├── requests.py          # Request models
│   └── responses.py         # Response models
├── mcts/                     # MCTS implementations
├── tree/                     # Tree structure
└── utils/                    # Utilities
```

### Service Components

- **MCTS Service**: Manages phase execution and orchestration
- **Session Service**: Handles search session lifecycle
- **Task Service**: Coordinates asynchronous task processing
- **Phase Registry**: Pluggable phase strategy system
- **Tree Framework**: Search tree data structures and operations

## API Reference

### Interactive Documentation

- **Swagger UI**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **ReDoc**: [http://localhost:8002/redoc](http://localhost:8002/redoc)

### Core Endpoints

#### Session Management

**Create Search Session**
```http
POST /sessions
Content-Type: application/json

{
  "tree_config": {
    "concepts": ["arrays", "sorting"],
    "difficulties": ["easy", "medium", "hard"]
  }
}
```

#### Phase Execution

**Run MCTS Phase**
```http
POST /sessions/{session_id}/phases/{phase_name}
Content-Type: application/json

{
  "phase_config": {
    "max_iterations": 50,
    "convergence_checks": 3
  }
}
```

#### Tree Operations

**Get Tree Structure**
```http
GET /sessions/{session_id}/tree
```

**Get Tree Statistics**
```http
GET /sessions/{session_id}/tree/stats
```

## MCTS Implementation

### Phase Registry System

The service uses a decorator-based registry for pluggable phase strategies:

```python
from mcts.phase_registry import phase_registry

@phase_registry.register_phase_method("custom_phase", "select_node")
async def select_node(self: "BasePhase") -> ChallengeNode:
    """Custom node selection strategy"""
    # Your implementation here
    pass
```

### Built-in Phases

#### Phase 1: Initial Capability Mapping
- **Selection**: Probability-based selection favoring less-explored nodes
- **Expansion**: Concept combination or difficulty progression
- **Scoring**: Success-based with difficulty multipliers
- **Objective**: Map model capabilities across concept space

#### Phase 2: Challenge Discovery  
- **Selection**: Same as Phase 1 with different exploration parameters
- **Expansion**: Focus on challenging combinations
- **Scoring**: Inverted scoring - higher values for failures
- **Objective**: Identify areas where model struggles

#### Phase 3: Comprehensive Evaluation
- **Selection**: Restricted to Phase 2 nodes above threshold
- **Expansion**: Generate variations of challenging problems
- **Scoring**: Challenge-based scoring
- **Objective**: Deep evaluation of difficult areas

### Tree Structure

```python
class ChallengeNode:
    """Node in the MCTS tree representing a challenge configuration"""

    def __init__(self, concepts: List[str], difficulty: str):
        self.concepts = concepts
        self.difficulty = difficulty
        self.visits = 0
        self.value = 0.0
        self.children = []
        self.parent = None

    def ucb1(self, exploration_constant: float = 1.414) -> float:
        """Calculate UCB1 score for node selection"""
        # Implementation details...
```

## Configuration

### Phase Configuration

Each phase can be configured independently:

```yaml
phase1:
  phase_params:
    max_depth: 5
    max_iterations: 100
    performance_threshold: 0.4
    value_delta_threshold: 0.3
    convergence_checks: 5
    exploration_probability: 0.2
    num_nodes_per_iteration: 5
    task_timeout: 90.0

  search_params:
    exploration_weight: 1.414
    discount_factor: 0.95

  scoring_params:
    penalty_per_failure: -0.1
    penalty_per_error: -0.15
    penalty_per_attempt: -0.05
    fixed_by_problem_fixer_penalty: -0.2
    max_num_passed: 10

  environment:
    environment_name: "environment_coding_challenge"
    llm_service_url: "http://llm-interface:8000"
    timeout: 300
```

### Tree Configuration

```yaml
tree_configs:
  concepts:
    - "arrays"
    - "sorting"
    - "dynamic_programming"
    - "graph_algorithms"
    - "tree_traversal"

  difficulties:
    - "very easy"
    - "easy"
    - "medium"
    - "hard"
    - "veryhard"
```

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests
pytest
```

### Adding Custom Phases

1. **Create phase module** in `src/mcts/`
2. **Register phase methods** using decorators
3. **Add configuration** to `params.yml`
4. **Update documentation**

Example custom phase:

```python
# src/mcts/my_custom_phase.py
from typing import TYPE_CHECKING
from .phase_registry import phase_registry

if TYPE_CHECKING:
    from .base_phase import BasePhase

@phase_registry.register_phase_method("my_custom_phase", "select_node")
async def select_node(self: "BasePhase") -> ChallengeNode:
    """Custom node selection logic"""
    # Your implementation
    pass

@phase_registry.register_phase_method("my_custom_phase", "expand_node")
async def expand_node(self: "BasePhase", node: ChallengeNode) -> None:
    """Custom node expansion logic"""
    # Your implementation
    pass
```

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

Monitor phase execution:

```bash
# Watch logs in real-time
tail -f logs/search_service.log
```

## Advanced Usage

### Multi-Phase Execution

```python
from services.mcts_service import MCTSService
from tree import Tree

# Initialize
service = MCTSService(settings)
tree = Tree(concepts=["arrays", "sorting"], difficulties=["easy", "medium"])

# Run phase sequence
await service.run_multiple_phases(
    phase_sequence=["phase_1", "phase_2", "phase_3"],
    tree=tree,
    task=task
)
```

### Custom Environment Integration

```python
from environment_client import EnvironmentClient

# Configure custom environment
environment = EnvironmentClient({
    "environment_name": "my_custom_environment",
    "llm_service_url": "http://llm-interface:8000",
    "timeout": 300
})

# Use in phase execution
phase = create_phase("phase_1", tree, environment, config)
await phase.run()
```

### Tree Analysis

```python
# Analyze tree structure
def analyze_tree(tree: Tree):
    stats = {
        "total_nodes": len(tree.nodes),
        "max_depth": max(node.depth for node in tree.nodes),
        "concepts_explored": set(concept for node in tree.nodes for concept in node.concepts),
        "avg_node_value": sum(node.value for node in tree.nodes) / len(tree.nodes)
    }
    return stats
```

---

### Related Documentation

- [Multi-Phase MCTS Framework](src/mcts/README.md) - Deep dive into MCTS implementation
- [Tree Structure Framework](src/tree/README.md) - Tree data structures and operations  
- [Search Service API](src/api/README.md) - Complete API reference

For more information, see the [main PrismBench documentation](../../../docs/).
