from typing import Dict

from loguru import logger

from ..core.config import Settings
from ..core.exceptions import EnvironmentExecutionException
from ..environment.environment_registry import environment_registry
from ..environment.utils import create_environment
from ..models.requests import ChallengeRequest


class EnvironmentService:
    """Service for managing coding challenge environments."""

    def __init__(self, settings: Settings):
        """
        Initialize the environment service.

        Args:
            settings: Application settings
        """
        self.settings = settings

        # automatically load all environment modules
        environment_registry.load_environment_modules()

        # get all available environments
        self.environments = environment_registry.list_environments()
        logger.info(f"Available environments: {self.environments}")

    def _get_environment_config(self, environment_name: str) -> Dict:
        """
        Get configuration for a specific environment.

        Args:
            environment_name: Name of the environment (e.g., 'environment_coding_challenge')

        Returns:
            Environment configuration dictionary
        """
        if hasattr(self.settings, "environment_configs") and self.settings.environment_configs:
            if environment_name in self.settings.environment_configs:
                config = self.settings.environment_configs[environment_name]
                return {
                    "agents": config.agents,
                    "max_attempts": config.max_attempts,
                    "timeout": config.timeout,
                    "num_problems": config.num_problems,
                }
            else:
                logger.warning(f"No environment config found for {environment_name}")
                return {}
        else:
            logger.warning("No environment configs loaded")
            return {}

    async def run_challenge(self, environment_name: str, request: ChallengeRequest) -> Dict:
        """
        Run a challenge using the specified environment.

        Args:
            environment_name: Name of the environment to use
            request: Challenge request parameters

        Returns:
            Dict: Challenge execution results

        Raises:
            EnvironmentExecutionException: If challenge execution fails
        """
        if environment_name not in self.environments:
            raise EnvironmentExecutionException(
                f"Environment '{environment_name}' not found. Available: {list(self.environments.keys())}"
            )

        try:
            logger.info(f"Running challenge using environment: {environment_name}")
            logger.info(f"Challenge parameters: {request.concept} - {request.difficulty_level}")

            # Get environment configuration
            env_config = self._get_environment_config(environment_name)

            if not env_config.get("agents"):
                raise EnvironmentExecutionException(f"No agents configured for environment {environment_name}")

            # Create environment
            env = create_environment(
                environment_name,
                agents=env_config["agents"],
            )

            # Prepare execution parameters using environment config defaults, with request overrides
            execution_params = {
                "concept": request.concept,
                "difficulty_level": request.difficulty_level,
                "max_attempts": request.max_attempts or env_config.get("max_attempts", 3),
                "previous_problems": request.previous_problems if request.previous_problems else [],
            }

            # Add num_problems parameter if the environment supports it
            if env_config.get("num_problems", 1) > 1:
                execution_params["num_problems"] = env_config["num_problems"]

            # Execute the challenge
            results = await env.execute_node(**execution_params)

            logger.info(
                f"Challenge completed with success: {results.get('success', False) if hasattr(results, 'get') else getattr(results, 'success', 'N/A')}"
            )
            return results

        except Exception as e:
            logger.exception(f"Error running challenge with environment {environment_name}: {str(e)}")
            raise EnvironmentExecutionException(f"Challenge execution failed: {str(e)}")
