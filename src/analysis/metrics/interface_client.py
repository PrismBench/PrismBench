import pprint
import uuid
from typing import Optional

import httpx
from loguru import logger


class InterfaceClient:
    """Client for interacting with the LLM Interface Service."""

    def __init__(
        self,
        base_url: str,
        role: str,
        timeout: int = 300,
    ):
        """
        Initialize the LLM client.

        Args:
            base_url (str): Base URL of the LLM interface service
            role (str): Role to use for this interaction
            timeout (int): Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.role = role
        self.session_id = None
        self._initialized = False

    async def initialize(self):
        """
        Initialize a session with the LLM interface service.

        Returns:
            None
        """
        if self._initialized:
            logger.info(f"Session already initialized: {self.session_id}")
            return self.session_id

        self.session_id = str(uuid.uuid4())
        self._initialized = True

        logger.info(f"Session initialized: {self.session_id}")

    async def interact(self, **kwargs) -> Optional[str]:
        """
        Interact with the LLM service.

        Args:
            **kwargs: Input data for the interaction

        Returns:
            Optional[str]: Response from the LLM
        """
        if not self._initialized:
            await self.initialize()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Start the interaction
                logger.info(f"Interacting with {self.role} - {self.session_id}")
                logger.debug(f"Input data: {pprint.pformat(kwargs)}")
                response = await client.post(
                    f"{self.base_url}/interact",
                    json={
                        "session_id": self.session_id,
                        "input_data": kwargs,
                        "role": self.role,
                        "use_agent": False,
                    },
                )
                response.raise_for_status()
                data = response.json()

                logger.debug(f"Status response: {response}")
                return data["message"]

        except Exception as e:
            logger.opt(exception=e).error(f"Error in LLM interaction: {e}")
            return None

    async def clear_memory(self) -> bool:
        """
        Clear the conversation history.

        Returns:
            bool: True if successful
        """
        if not self._initialized:
            return False

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/clear_memory/{self.session_id}",
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False

    async def close(self) -> bool:
        """
        Close the session and cleanup.

        Returns:
            bool: True if successful
        """
        if not self._initialized:
            return True

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(f"{self.base_url}/session/{self.session_id}")
                response.raise_for_status()
                self._initialized = False
                return True
        except Exception as e:
            logger.error(f"Error closing session: {e}")
            return False
