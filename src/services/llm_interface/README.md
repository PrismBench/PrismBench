# LLM Interface Service

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-🦜-green.svg)](https://langchain.com)

> A FastAPI-based microservice for interacting with LLMs through a unified, extensible interface. Supports both direct LLM chat and agentic workflows, with modular configuration and robust async processing.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Development](#development)
- [Examples](#examples)
- [Deployment](#deployment)

## Features

- **Unified API** for multiple LLM providers (OpenAI, Anthropic, DeepSeek, Together, Local, etc.)
- **Session management** for multi-turn conversations
- **Agent support** via LangChain tools
- **Async request processing** with task status tracking
- **Configurable prompts and roles** via YAML
- **Comprehensive OpenAPI docs** with examples
- **CORS support** for easy integration

## Quick Start

### Prerequisites
- Python 3.12+
- Redis (for session storage)
- API keys for your preferred LLM providers

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys (see Configuration section)
cp apis.key.example apis.key
# Edit apis.key with your API keys

# Run the service
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Installation

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "llm_interface"
}
```

## API Reference

### Interactive Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Core Endpoints

#### Session Management

**Initialize a Session**
```http
POST /initialize
Content-Type: application/json

{
  "role": "problem_solver"
}
```

**Response:**
```json
{
  "message": "Session initialized successfully",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### LLM Interaction

**Interact with LLM**
```http
POST /interact
Content-Type: application/json

{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "input_data": {"input_text": "What is the capital of France?"},
  "use_agent": false
}
```

**Response:**
```json
{
  "message": "Request is being processed asynchronously",
  "task_id": "123e4567-e89b-12d3-a456-426614174001",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Task Status

**Check Task Status**
```http
GET /task_status/{task_id}
```

**Response (completed):**
```json
{
  "status": "completed",
  "result": {"response": "Paris is the capital of France."}
}
```

#### Conversation History

**Get Conversation History**
```http
GET /conversation_history/{session_id}
```

**Response:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "history": [
    {"role": "human", "content": "What is the capital of France?"},
    {"role": "ai", "content": "Paris is the capital of France."}
  ]
}
```

## Architecture

### Project Structure

```
llm_interface/
├── src/
│   ├── main.py                      # FastAPI app entrypoint
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/           # API endpoint modules
│   │       │   ├── health.py        # Health check endpoints
│   │       │   ├── history.py       # Conversation history endpoints
│   │       │   ├── interact.py      # LLM interaction endpoints
│   │       │   ├── sessions.py      # Session management endpoints
│   │       │   └── tasks.py         # Task status endpoints
│   │       └── router.py            # API route aggregation
│   ├── core/
│   │   ├── config.py                # Application configuration
│   │   ├── dependencies.py          # Dependency injection
│   │   └── exceptions.py            # Custom exceptions
│   ├── llm/
│   │   ├── interface.py             # LLM interface logic
│   │   ├── prompt_manager.py        # Prompt/config management
│   │   └── tools.py                 # LangChain tools
│   ├── models/
│   │   ├── domain.py                # Domain models
│   │   ├── requests.py              # Request schemas
│   │   └── responses.py             # Response schemas
│   ├── repositories/
│   │   ├── session_repo.py          # Session data access
│   │   └── task_repo.py             # Task data access
│   ├── services/
│   │   ├── interaction_service.py   # Interaction business logic
│   │   └── session_service.py       # Session business logic
│   └── redis_store.py               # Redis storage utilities
├── configs/
│   └── agents/                      # YAML configs for agent roles
├── requirements.txt                 # Python dependencies
├── requirements.in                  # Dependencies source file
├── Dockerfile                       # Containerization
├── .dockerignore                    # Docker ignore patterns
├── test.py                          # API test script
└── README.md                        # This file
```

### Core Components

- **FastAPI App**: Modern async web framework with automatic API docs
- **LLM Interface**: Unified abstraction over multiple LLM providers
- **Session Management**: Redis-backed session storage with conversation history
- **Task Processing**: Asynchronous request processing with status tracking
- **Agent Support**: LangChain integration for tool-using agents

## Configuration

### API Keys

Create an `apis.key` file in the project root:

```bash
OPENAI_API_KEY = sk-your-openai-key-here
ANTHROPIC_API_KEY = your-anthropic-key-here
DEEPSEEK_API_KEY = your-deepseek-key-here
CHATLAMMA_API_KEY = your-chatlamma-key-here
LOCAL = your-local-api-key-or-token  # For ollama/LMstudio
```

### Agent Configuration

Place YAML configuration files in `configs/agents/` directory. Each file defines an agent role:

```yaml
# configs/agents/problem_solver.yml
name: "problem_solver"
model_name: "gpt-4o-mini"
provider: "openai"
system_prompt: "You are an expert problem solver..."
interaction_templates:
  default:
    input_template: "Problem: {input_text}"
    output_template: "{response}"
```

### Environment Variables

- **API keys**: Set via `apis.key` or environment variables (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)
- **CORS**: All origins allowed by default (see `main.py` to restrict)
- **Redis**: Configure Redis connection via standard environment variables

## Development

### Running Tests

```bash
# Run API tests
python test.py
```

### Code Style

```bash
# Format code
black src/
flake8 src/
```

### Adding New Providers

1. Extend the `LLMInterface._create_llm_instance()` method
2. Add provider configuration to `_initialize_providers()`
3. Update documentation

## Examples

### Basic Usage

```python
from src.llm.interface import LLMInterface

# Initialize interface
llm = LLMInterface.from_config_file("configs/agents/problem_solver.yml")

# Interact with LLM
response = llm.interact(input_text="What is Python?")
print(response)
```

### Session-based Conversation

```python
import requests

# Initialize session
response = requests.post("http://localhost:8000/initialize", 
                        json={"role": "problem_solver"})
session_id = response.json()["session_id"]

# Multi-turn conversation
requests.post("http://localhost:8000/interact", 
             json={
                 "session_id": session_id,
                 "input_data": {"input_text": "What is Python?"},
                 "use_agent": False
             })
```

## Deployment

### Docker

**Build and run:**
```bash
docker build -t llm-interface .
docker run -p 8000:8000 --env-file apis.key llm-interface
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  llm-interface:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - apis.key
    depends_on:
      - redis
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Production

For production deployment, consider:
- Using a production WSGI server (Gunicorn + Uvicorn workers)
- Setting up proper Redis persistence
- Configuring logging and monitoring
- Implementing rate limiting
- Setting up load balancing for multiple instances

## API Testing

Use the included test script:

```bash
python test.py
```

This will test:
- Health endpoint
- Session initialization 
- LLM interaction
- Task status checking
- Conversation history retrieval

---

For more information, see the [main PrismBench documentation](../../../docs/).
