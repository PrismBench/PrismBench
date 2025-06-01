# Search Service API

This document provides a comprehensive overview of the Search Service API endpoints.

## Endpoints Overview

### Health Check
- `GET /health` - Service health status

### Session Management
- `POST /initialize` - Initialize a new search session
- `GET /sessions/{session_id}` - Get session information

### Task Management
- `POST /run` - Start MCTS execution
- `POST /stop/{task_id}` - Stop a running task
- `GET /status` - Get status of all tasks
- `GET /tasks/{task_id}` - Get specific task status

### Tree Data
- `GET /tree/{session_id}` - Get MCTS tree data for a session

---

## Detailed Endpoint Documentation

### Health Check

#### `GET /health`
Check if the search service is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "service": "search"
}
```

**Status Codes:**
- `200` - Service is healthy

---

### Session Management

#### `POST /initialize`
Initialize a new search tree session or retrieve an existing one.

**Request Body:**
```json
{
  "session_id": "string"
}
```

**Response:**
```json
{
  "session_id": "string",
  "message": "Session initialized successfully",
  "tree_size": 0
}
```

**Status Codes:**
- `200` - Session initialized successfully
- `409` - Session already exists
- `500` - Server error during initialization

#### `GET /sessions/{session_id}`
Get information about a specific session.

**Parameters:**
- `session_id` (path) - The session identifier

**Response:**
```json
{
  "session_id": "string",
  "message": "Session found",
  "tree_size": 42
}
```

**Status Codes:**
- `200` - Session information retrieved successfully
- `404` - Session not found
- `500` - Server error

---

### Task Management

#### `POST /run`
Start MCTS execution asynchronously. Returns immediately with a task ID for tracking.

**Request Body (Optional):**
```json
{
  "session_id": "string"
}
```

If no `session_id` is provided, a new one will be generated automatically.

**Response:**
```json
{
  "task_id": "string",
  "session_id": "string", 
  "message": "Request is being processed asynchronously",
  "phases": {
    "phase_name": {
      "status": "pending|running|completed|failed|cancelled",
      "created_at": "2024-01-01T00:00:00",
      "started_at": "2024-01-01T00:00:00",
      "completed_at": "2024-01-01T00:00:00",
      "cancelled_at": "2024-01-01T00:00:00",
      "error": "string",
      "path": "string"
    }
  }
}
```

**Status Codes:**
- `202` - Request accepted and being processed
- `404` - Session not found
- `500` - Server error during task creation

#### `POST /stop/{task_id}`
Stop a running MCTS task and cancel any pending phases.

**Parameters:**
- `task_id` (path) - The task identifier to stop

**Response:**
```json
{
  "task_id": "string",
  "session_id": "string",
  "message": "Task cancelled successfully",
  "phases": {
    "phase_name": {
      "status": "cancelled",
      "created_at": "2024-01-01T00:00:00",
      "started_at": "2024-01-01T00:00:00",
      "completed_at": null,
      "cancelled_at": "2024-01-01T00:00:00",
      "error": null,
      "path": "string"
    }
  }
}
```

**Status Codes:**
- `200` - Task stopped successfully
- `404` - Task not found
- `400` - Task cannot be stopped (already completed or failed)
- `500` - Server error during task cancellation

#### `GET /status`
Get the status of all tasks in the system.

**Response:**
```json
{
  "message": "No tasks found",
  "tasks": {
    "task_id": {
      "status": "running",
      "session_id": "string",
      "phases": {...}
    }
  }
}
```

**Status Codes:**
- `200` - Task status retrieved successfully
- `500` - Server error during status retrieval

#### `GET /tasks/{task_id}`
Get the status of a specific task.

**Parameters:**
- `task_id` (path) - The task identifier

**Response:**
```json
{
  "task_id": "string",
  "session_id": "string",
  "message": "Task status: running",
  "phases": {
    "phase_name": {
      "status": "running",
      "created_at": "2024-01-01T00:00:00",
      "started_at": "2024-01-01T00:00:00",
      "completed_at": null,
      "cancelled_at": null,
      "error": null,
      "path": "string"
    }
  }
}
```

**Status Codes:**
- `200` - Task status retrieved successfully
- `404` - Task not found
- `500` - Server error during status retrieval

---

### Tree Data

#### `GET /tree/{session_id}`
Retrieve the current state of the MCTS tree for a given session.

**Parameters:**
- `session_id` (path) - The session identifier

**Response:**
```json
{
  "session_id": "string",
  "tree": {
    "nodes": {...},
    "edges": {...},
    "metadata": {...}
  },
  "statistics": {
    "total_nodes": 42,
    "depth": 5,
    "last_updated": "2024-01-01T00:00:00"
  }
}
```

**Status Codes:**
- `200` - Tree data successfully retrieved
- `404` - Session ID not found
- `500` - Error serializing tree data

---

## Usage Examples

### Starting a New MCTS Session

1. **Initialize a session:**
```bash
curl -X POST "http://localhost:8000/initialize" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my-session-123"}'
```

2. **Start MCTS execution:**
```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my-session-123"}'
```

3. **Check task status:**
```bash
curl "http://localhost:8000/tasks/{task_id}"
```

4. **Get tree data:**
```bash
curl "http://localhost:8000/tree/my-session-123"
```

### Monitoring and Control

- **Check service health:**
```bash
curl "http://localhost:8000/health"
```

- **Get all task statuses:**
```bash
curl "http://localhost:8000/status"
```

- **Stop a running task:**
```bash
curl -X POST "http://localhost:8000/stop/{task_id}"
```

---

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

- `200` - Success
- `202` - Accepted (for async operations)
- `400` - Bad Request
- `404` - Not Found
- `409` - Conflict (resource already exists)
- `500` - Internal Server Error

Error responses include a `detail` field with a descriptive error message.

---
