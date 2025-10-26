# LLM Interface Service

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
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
uv pip install -e .

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

**Delete a session**
```http
DELETE /session/{session_id}
Content-Type: application/json
```

**Response:**
```json
{
  "message": "Session {session_id} deleted"
}
```

#### LLM Interaction

**Interact with LLM**
```http
POST /interact
Content-Type: application/json

{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "input_data": {
    "concepts": [
      "recursion",
      "dynamic programming"
    ],
    "difficulty_level": "medium"
  },
  "role": "challenge_designer",
  "use_agent": false
}

```

**Response:**
```json
{
  "message": "Response from LLM",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Conversation History

**Get all active sessions**
```http
GET /active_sessions
Content-Type: application/json

{
  "role": "problem_solver"
}
```

**Response:**
```json
{
  "additionalProp1": {
    "additionalProp1": {}
  },
  "additionalProp2": {
    "additionalProp1": {}
  },
  "additionalProp3": {
    "additionalProp1": {}
  }
}
```

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
│   │       │   └── sessions.py      # Session management endpoints
│   │       └── router.py            # API route aggregation
│   ├── core/
│   │   ├── config.py                # Application configuration
│   │   ├── dependencies.py          # Dependency injection
│   │   └── exceptions.py            # Custom exceptions
│   ├── llm/
│   │   ├── interface.py             # LLM interface logic
│   │   └── utils.py                 # LangChain tools
│   ├── models/
│   │   ├── domain.py                # Domain models
│   │   ├── requests.py              # Request schemas
│   │   └── responses.py             # Response schemas
│   ├── repositories/
│   │   └──  session_repo.py          # Session data access
│   ├── services/
│   │   └── session_service.py       # Session business logic
├── pyproject.toml                   # Dependencies
├── Dockerfile                       # Containerization
├── .dockerignore                    # Docker ignore patterns
└── README.md                        # This file
```

### Core Components

- **FastAPI App**: Modern async web framework with automatic API docs
- **LLM Interface**: Unified abstraction over multiple LLM providers
- **Session Management**: Redis-backed session storage with conversation history
- **Agent Support**: Dspy integration for tool-using agents

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
role: challenge_designer

interaction_templates:
  default:
    inputs:
      - name: concepts
        type: list[str]
        description: A list of programming concepts. it can contain a single concept or multiple concepts
      - name: difficulty_level
        type: str
        description: A single string from one of the following options [very easy, easy, medium, hard, very hard]
    outputs:
      - name: response
        type: str
        description: The generated challenge in yaml format.

model_name: gpt-4o-mini
model_provider: openai
model_params:
  temperature: 0.8
  max_tokens: 5120

system_prompt: >
  When given a list of CS concepts and a difficulty level, design a programming challenge similar to LeetCode challenges based on the provided CS concepts.
  The difficulty levels are: [very easy, easy, medium, hard, very hard].

  The generated_challenge should have the following fields:
  - Problem Name: The name of the problem
  - Concepts: The specified concepts
  - Difficulty Level: The specified difficulty level
  - Problem Statement: A clear and concise problem statement
  - Input Format: Input format specification including the input types and constraints
  - Output Format: Output format specification including the output types and constraints
  - Constraints: Constraints on input and ouput values
  - Examples: At least two examples with input and expected output
  - Relevance to Concepts: A brief explanation of the concept's relevance to the problem

  Note: do NOT include the ```yaml``` tags in the output. only return the yaml format.
```

### Environment Variables

- **API keys**: Set via `apis.key` or environment variables (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)
- **CORS**: All origins allowed by default (see `main.py` to restrict)
- **Redis**: Configure Redis connection via standard environment variables

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

---

For more information, see the [main PrismBench documentation](../../../docs/).
