import os
from typing import Any, Dict

import httpx
from loguru import logger


class EnvironmentClient:
    """Client for interacting with the Environment Service API."""

    def __init__(
        self,
        config: Dict[str, Any],
        timeout: int = 60,
    ):
        """
        Initialize the environment client.

        Args:
            config (Dict[str, Any]): Configuration dictionary
            timeout (int): Request timeout in seconds
        """
        self.config = config

        self.name = config.get("name", "environment_coding_challenge")
        self.base_url = (
            config.get("base_url", os.getenv("ENV_SERVICE_URL", "http://node-env:8000"))
            if not config.get("base_url")
            else config.get("base_url")
        )

        logger.info(f"Base URL for Environment Client: {self.base_url}")
        logger.info(f"Environment name: {self.name}")

        self.timeout = timeout

    async def run_challenge(self, **kwargs) -> Dict[str, Any]:
        """
        Run a coding challenge via the environment service API.

        Args:
            **kwargs: Challenge parameters including concept, difficulty_level, max_attempts

        Returns:
            Dict[str, Any]: Challenge results
        """
        try:
            # Extract parameters for the request body (only valid ChallengeRequest fields)
            request_body = {}

            # Required parameters
            if "concept" in kwargs:
                request_body["concept"] = kwargs["concept"]
            if "difficulty_level" in kwargs:
                request_body["difficulty_level"] = kwargs["difficulty_level"]

            # Optional parameters
            if "max_attempts" in kwargs:
                request_body["max_attempts"] = kwargs["max_attempts"]

            # Use environment name from config as query parameter
            params = {"environment_name": self.name}

            logger.debug(f"Running challenge with environment '{self.name}' and request: {request_body}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/run-challenge", json=request_body, params=params)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error calling environment service: {e}")
            # Return a failed result structure
            return {"success": False, "data_trail": [], "error": str(e)}
