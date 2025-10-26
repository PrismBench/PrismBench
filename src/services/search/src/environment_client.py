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
        # TODO:fix this to load from environment settings config later
        self.timeout = 300

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
            if "previous_problems" in kwargs:
                request_body["previous_problems"] = kwargs["previous_problems"]

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

        except httpx.TimeoutException as e:
            error_msg = f"Timeout error after {self.timeout}s when calling {self.base_url}/run-challenge"
            logger.error(f"{error_msg}: {e}")
            return {"success": False, "data_trail": [], "error": error_msg}
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code} error from environment service"
            response_text = getattr(e.response, "text", "No response text available")
            logger.error(f"{error_msg}. Response: {response_text}")
            return {"success": False, "data_trail": [], "error": f"{error_msg}: {response_text}"}
        except httpx.RequestError as e:
            error_msg = f"Network error when calling environment service at {self.base_url}"
            logger.error(f"{error_msg}: {type(e).__name__} - {e}")
            return {"success": False, "data_trail": [], "error": f"{error_msg}: {type(e).__name__}"}
        except ValueError as e:
            error_msg = "Invalid JSON response from environment service"
            logger.error(f"{error_msg}: {e}")
            return {"success": False, "data_trail": [], "error": error_msg}
        except Exception as e:
            error_msg = "Unexpected error calling environment service"
            logger.error(f"{error_msg}: {type(e).__name__} - {e if str(e) else 'No error message available'}")
            return {"success": False, "data_trail": [], "error": f"{error_msg}: {type(e).__name__}"}
