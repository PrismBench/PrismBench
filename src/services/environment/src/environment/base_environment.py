import os
import uuid
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, Dict

from loguru import logger

from ..environment.environment_registry import environment_registry
from ..interface_client import InterfaceClient


class BaseEnvironment:
    """
    A base class for all environments.
    Contains common methods and attributes shared by Environment variants.
    """

    def __init__(
        self,
        environment_name: str,
        **kwargs,
    ) -> None:
        """
        Initialize the BaseEnvironment class.

        Args:
            environment_name (str): The name of the environment to use.
            **kwargs: Additional arguments passed to the environment.

        Raises:
            ValueError: If no agents are provided for the environment.
        """
        self.environment_name = environment_name
        self.llm_base_url = os.getenv("LLM_SERVICE_URL", "http://llm-interface:8000")
        self.challenge_id = str(uuid.uuid4())

        # create the output directory for the environment
        self.output_dir = os.path.join(
            os.getenv("ENV_OUTPUT_DIR", "/app/env_outputs"),
            self.challenge_id,
        )
        os.makedirs(
            self.output_dir,
            exist_ok=True,
        )
        # create a process pool for parallel execution
        self._pool = ProcessPoolExecutor()

        # set the agents for the environment
        if kwargs:
            self.agents = {
                agent: InterfaceClient(
                    base_url=self.llm_base_url,
                    role=agent,
                )
                for agent in kwargs.get("agents", [])
            }
        else:
            self.agents = {}
            logger.error(f"No agents provided for environment {environment_name}")
            raise ValueError(f"No agents provided for environment {environment_name}")

        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize all agents asynchronously.

        Returns:
            None
        """
        logger.debug(f"Initializing environment {self.environment_name}")
        logger.debug(f"Agents: {self.agents}")

        if self._initialized:
            return

        # set roles for each agent
        for agent in self.agents.values():
            await agent.initialize()

        self._initialized = True

    def __del__(self) -> None:
        """
        Cleanup temporary files when the instance is destroyed.

        Returns:
            None
        """
        try:
            if hasattr(self, "_pool"):
                self._pool.shutdown(wait=False, cancel_futures=True)
        except Exception as e:
            logger.error(f"Error shutting down process pool: {e}")

        try:
            if os.path.exists(self.output_dir):
                for file in os.listdir(self.output_dir):
                    try:
                        os.remove(os.path.join(self.output_dir, file))
                    except Exception as e:
                        logger.error(f"Error removing file {file}: {e}")
                os.rmdir(self.output_dir)

        except Exception as e:
            logger.error(f"Error cleaning up output directory: {e}")

    async def execute_node(self, **kwargs) -> Dict:
        """
        Execute a node in the environment.

        This method is used to execute a node in the environment.
        It will use the strategy method to execute the node.
        The strategy method is determined by the strategy_name.

        Args:
            **kwargs: Additional arguments passed to the environment.

        Returns:
            Dict: The results of the node execution.

        Raises:
            NotImplementedError: If no strategy is found for the method.
            Exception: If an error occurs while executing the node.
        """
        environment_method = self._get_environment_method("execute_node")

        try:
            return await environment_method(self, **kwargs)
        except Exception as e:
            logger.exception(f"Error executing node: {e}")
            raise

    def _get_environment_method(self, method_name: str) -> Callable:
        """
        Get a environment method, either from registry or raise an error.

        Args:
            method_name (str): Name of the method to get

        Returns:
            Callable: The environment method

        Raises:
            NotImplementedError: If no environment is found for the method
        """
        if self.environment_name:
            strategy_method = environment_registry.get_environment_method(self.environment_name, method_name)
            if strategy_method:
                return strategy_method

        raise NotImplementedError(
            f"No environment found for {method_name}. "
            f"Either implement it in a subclass or register it using "
            f"@environment_registry.register_environment('{self.environment_name}', '{method_name}')"
        )

    async def reset(self) -> None:
        """
        Clear the memory of all agents.

        Returns:
            None
        """

        # close existing sessions
        for agent in self.agents.values():
            await agent.close()

        logger.debug("Agents Restarted.")
