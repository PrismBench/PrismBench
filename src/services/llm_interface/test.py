#!/usr/bin/env python3
"""
Test script for the LLM Interface API.
This script tests the basic functionality of the API endpoints.
"""

import json
import time
import uuid
from typing import Any, Dict

import requests

BASE_URL = "http://localhost:8000"


def test_health() -> Dict[str, Any]:
    """Test the health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()
    return response.json()


def test_initialize() -> Dict[str, Any]:
    """Test the initialize endpoint."""
    session_id = str(uuid.uuid4())
    print(f"Initializing session: {session_id}")

    response = requests.post(f"{BASE_URL}/initialize", json={"session_id": session_id})

    print(f"Initialize: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

    return {"session_id": session_id, "response": response.json()}


def test_set_role(session_id: str, role: str) -> Dict[str, Any]:
    """Test the set_role endpoint."""
    print(f"Setting role to '{role}' for session: {session_id}")

    response = requests.post(
        f"{BASE_URL}/set_role", json={"session_id": session_id, "role": role}
    )

    print(f"Set role: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

    return response.json()


def test_interact(
    session_id: str, input_text: str, use_agent: bool = False
) -> Dict[str, Any]:
    """
    Test the interact endpoint.

    Args:
        session_id: The session ID to interact with
        input_text: The text input to send to the LLM
        use_agent: Whether to use agent mode

    Returns:
        Dict containing the response data including task_id
    """
    print(f"Interacting with session: {session_id}")
    print(f"Input: {input_text}")
    print(f"Using agent: {use_agent}")

    response = requests.post(
        f"{BASE_URL}/interact",
        json={
            "session_id": session_id,
            "input_data": {
                "concepts": "binary search tree",
                "difficulty_level": "medium",
            },
            "use_agent": use_agent,
        },
    )

    print(f"Interact: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

    return response.json()


def test_task_status(
    task_id: str, max_retries: int = 10, retry_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Test the task_status endpoint with polling until completion.

    Args:
        task_id: The task ID to check status for
        max_retries: Maximum number of status check attempts
        retry_delay: Delay between status checks in seconds

    Returns:
        Dict containing the final task result or status
    """
    print(f"Checking status for task: {task_id}")

    for attempt in range(max_retries):
        response = requests.get(f"{BASE_URL}/task_status/{task_id}")
        status_data = response.json()

        print(
            f"Task status (attempt {attempt + 1}/{max_retries}): {response.status_code}"
        )
        print(json.dumps(status_data, indent=2))

        # If the task is completed or failed, return the result
        if "status" not in status_data or status_data["status"] != "processing":
            print(f"Task completed with result: {status_data}")
            print()
            return status_data

        print(f"Task still processing, waiting {retry_delay} seconds...")
        time.sleep(retry_delay)

    print("Max retries reached, task did not complete in time")
    print()
    return {"status": "timeout", "error": "Task did not complete in time"}


def test_conversation_history(session_id: str) -> Dict[str, Any]:
    """Test the conversation_history endpoint."""
    print(f"Getting conversation history for session: {session_id}")

    response = requests.get(f"{BASE_URL}/conversation_history/{session_id}")

    print(f"Conversation history: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

    return response.json()


def test_clear_memory(session_id: str) -> Dict[str, Any]:
    """Test the clear_memory endpoint."""
    print(f"Clearing memory for session: {session_id}")

    response = requests.post(
        f"{BASE_URL}/clear_memory", json={"session_id": session_id}
    )

    print(f"Clear memory: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

    return response.json()


def test_delete_session(session_id: str) -> Dict[str, Any]:
    """Test the delete_session endpoint."""
    print(f"Deleting session: {session_id}")

    response = requests.delete(f"{BASE_URL}/session/{session_id}")

    print(f"Delete session: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

    return response.json()


def run_tests() -> None:
    """Run all tests for the LLM Interface API."""
    # Test health endpoint
    test_health()

    # Test initialize endpoint
    init_result = test_initialize()
    session_id = init_result["session_id"]
    available_roles = init_result["response"].get("available_roles", [])

    if available_roles:
        # Test set_role endpoint with the second available role
        test_set_role(session_id, available_roles[1])

        # Test interact endpoint with regular mode
        interact_result = test_interact(session_id, "Hello, how can you help me today?")

        # Check task status until completion
        if "task_id" in interact_result:
            task_id = interact_result["task_id"]
            test_task_status(task_id)

        # Test conversation history endpoint
        test_conversation_history(session_id)

        # Test clear memory endpoint
        test_clear_memory(session_id)

        # Test interact again after clearing memory
        post_clear_interact = test_interact(session_id, "What is your name?")

        # Check task status for post-clear interaction
        if "task_id" in post_clear_interact:
            post_clear_task_id = post_clear_interact["task_id"]
            test_task_status(post_clear_task_id)

        # Test conversation history again
        test_conversation_history(session_id)

    # Test delete session endpoint
    test_delete_session(session_id)


if __name__ == "__main__":
    run_tests()
