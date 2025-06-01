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
pip install -r requirements.txt
docker compose up
```

**📖 [See detailed setup guide →](docs/quickstart.md)**

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
│   └── interface/         # shadcdn-based interface for interacting with the framework
├── configs/              # Configuration files
└── docs/                # Comprehensive documentation wiki
```

## 📚 Documentation

> **🌟 [Visit our wiki →](docs/README.md)**

<table>
<tr>
<td width="50%">

### 🚀 **Getting Started**
- [📖 **Complete Wiki**](docs/README.md) - Comprehensive documentation
- [⚡ Quick Start Guide](docs/quickstart.md) - Get running in 5 minutes  
- [🏗️ Architecture Overview](docs/architecture.md) - System design
- [⚙️ Configuration Guide](docs/config-overview.md) - Setup and customization

</td>
<td width="50%">

### 🎯 **Core Concepts**
- [🧠 MCTS Algorithm](docs/mcts.md) - Core algorithm details
- [🤖 Agent System](docs/agents.md) - Multi-agent architecture
- [🌍 Environment System](docs/environments.md) - Evaluation environments
- [📊 Results Analysis](docs/analysis.md) - Understanding outputs

</td>
</tr>
</table>

### 🔧 **Component Documentation**

| Component | Purpose | Documentation |
|-----------|---------|---------------|
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