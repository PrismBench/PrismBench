# 🔬 PrismBench
> An LLM capability mapping framework for systematic evaluation of language models in computer science problem-solving

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license) [![Documentation](https://img.shields.io/badge/docs-wiki-green.svg)](docs/README.md) [![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](#requirements)

*This branch contains the updated PrismBench framework.*
For the replication package of the paper, please switch to [Replication Package](https://github.com/PrismBench/PrismBench/tree/replication-package) branch.

## What is PrismBench?

PrismBench systematically evaluates LLM models through a three-phase Monte Carlo Tree Search approach:
- **Phase 1**: Maps initial capabilities across CS concepts
- **Phase 2**: Discovers challenging concept combinations  
- **Phase 3**: Conducts comprehensive evaluation of weaknesses

## Quick Start

```bash
git clone https://github.com/PrismBench/PrismBench.git
cd PrismBench

# See all available commands
make help

# Set up the development environment
make setup

# Configure your API keys in apis.key, then start services
make start
```

Once running, the web interface is available at [http://localhost:3000](http://localhost:3000).

**📖 [See detailed setup guide →](docs/Quick-Start.md)**

## Key Features

- **Systematic Evaluation**: MCTS-driven exploration of model capabilities
- **Challenge Discovery**: Automatically identifies model weaknesses
- **Comprehensive Analysis**: Detailed performance metrics and insights
- **Containerized**: Easy deployment with Docker
- **API Compatible**: Works with any OpenAI-compatible API

## Architecture

```
PrismBench/
├── src/services/           # Core framework components
│   ├── llm_interface/     # LLM communication layer
│   ├── environment/       # Challenge execution environment  
│   ├── search/           # MCTS implementation
│   └── gui/              # shadcdn-based interface for interacting with the framework
├── configs/              # Configuration files
├── docs/                # Comprehensive documentation wiki
└── Dockerfile.base      # Shared base image for Python services
```

## 🐳 Docker Build Optimization

PrismBench uses a shared base image approach to optimize Docker builds:

- **Base Image**: `Dockerfile.base` contains common Python setup, system dependencies, and uv installation
- **Service Images**: Each Python service inherits from the base image, reducing build time and image size
- **Layer Caching**: Common dependencies are cached in the base image, speeding up subsequent builds

### Build Commands

```bash
# Build only the base image
make build-base

# Build all services (uses cached base image)
make build

# Rebuild base image from scratch
make rebuild-base

# Rebuild all services from scratch
make rebuild
```

## 📚 Documentation

> **🌟 [Visit our wiki →](https://github.com/PrismBench/PrismBench/wiki)**

<table>
<tr>
<td width="50%">

### 🚀 **Getting Started**
- [📖 **Complete Wiki**](https://github.com/PrismBench/PrismBench/wiki) - Comprehensive documentation
- [⚡ Quick Start Guide](https://github.com/PrismBench/PrismBench/wiki/Quick-Start) - Get running in 5 minutes  
- [🏗️ Architecture Overview](https://github.com/PrismBench/PrismBench/wiki/Architecture-Overview) - System design
- [⚙️ Configuration Guide](https://github.com/PrismBench/PrismBench/wiki/Configuration-Overview) - Setup and customization

</td>
<td width="50%">

### 🎯 **Core Concepts**
- [🧠 MCTS Algorithm](https://github.com/PrismBench/PrismBench/wiki/MCTS-Algorithm) - Core algorithm details
- [🤖 Agent System](https://github.com/PrismBench/PrismBench/wiki/Agent-System) - Multi-agent architecture
- [🌍 Environment System](https://github.com/PrismBench/PrismBench/wiki/Environment-System) - Evaluation environments
- [📊 Results Analysis](https://github.com/PrismBench/PrismBench/wiki/Results-Analysis) - Understanding outputs

</td>
</tr>
</table>

### 🔧 **Component Documentation**

| Component | Purpose | Documentation |
|-----------|---------|---------------|
| 🎨 **GUI** | Web interface for the framework | [📖 README](src/services/gui/README.md) |
| 🤖 **LLM Interface** | Model communication | [📖 README](src/services/llm_interface/README.md) |
| 🌍 **Environment** | Code execution | [📖 README](src/services/environment/README.md) |
| 🔍 **Search** | MCTS implementation | [📖 README](src/services/search/README.md) |
| 📊 **Analysis** | Results processing | [📖 README](src/analysis/README.md) |

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

[MIT License](LICENSE) - see LICENSE file for details.

## Citation

If you use PrismBench in your research, please cite:
```bibtex
@software{prismbench,
  title={PrismBench: LLM Capability Mapping Framework},
  author={anonymous},
  year={2025},
  url={https://github.com/PrismBench/PrismBench}
}
```