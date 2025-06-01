import importlib
from pathlib import Path
from typing import Callable, Dict, List, Optional

from loguru import logger


class EnvironmentRegistry:
    """Registry for environment strategies using decorators."""

    def __init__(self) -> None:
        """Initialize the registry with empty strategy collections."""
        self.environments: Dict[str, Dict[str, Callable]] = {}
        self._loaded_modules: List[str] = []

    def load_environment_modules(
        self,
        environments_directory: Optional[str] = None,
    ) -> List[str]:
        """
        Automatically import all discovered environment modules to register environments.

        Args:
            environments_directory (Optional[str]): Optional custom directory for environment modules

        Returns:
            List[str]: List of loaded environment module names
        """
        discovered_environments = self.discover_environments(environments_directory)
        loaded_environments = []

        for environment_module in discovered_environments:
            if environment_module not in self._loaded_modules:
                try:
                    # import the module to trigger environment registration
                    importlib.import_module(f"..{environment_module}", package=__name__)
                    loaded_environments.append(environment_module)
                    self._loaded_modules.append(environment_module)
                    logger.debug(f"Loaded environment module: {environment_module}")
                except ImportError as e:
                    logger.error(f"Failed to load environment module {environment_module}: {e}")

        logger.info(f"Successfully loaded {len(loaded_environments)} environment modules")
        logger.info(f"Available environments: {self.environments}")
        return loaded_environments

    def discover_environments(self, environments_directory: Optional[str] = None) -> List[str]:
        """
        Discover all environment modules in the specified directory.

        Args:
            environments_directory (Optional[str]): Optional custom directory for environment modules

        Returns:
            List[str]: List of discovered environment module names
        """
        if environments_directory is None:
            # default to the directory containing this file
            environments_directory = Path(__file__).parent
        else:
            environments_directory = Path(environments_directory)

        discovered_environments = []

        # look for environment_*.py files
        for file_path in environments_directory.glob("environment_*.py"):
            if "environment_registry.py" in file_path.name:
                continue
            if file_path.is_file() and not file_path.name.startswith("__"):
                module_name = file_path.stem
                discovered_environments.append(module_name)

        logger.info(f"Discovered environments: {discovered_environments}")
        return discovered_environments

    def register_environment_method(
        self,
        environment_name: str,
        method_name: str,
    ) -> Callable:
        """
        Decorator to register a environment method.

        Args:
            environment_name (str): Name of the environment (e.g., 'basic', 'enhanced')
            method_name (str): Name of the method being registered

        Returns:
            Callable: The decorator function
        """

        def decorator(func: Callable) -> Callable:
            if environment_name not in self.environments:
                self.environments[environment_name] = {}
            self.environments[environment_name][method_name] = func
            logger.debug(f"Registered {method_name} for environment {environment_name}")
            return func

        return decorator

    def get_environment_method(
        self,
        environment_name: str,
        method_name: str,
    ) -> Optional[Callable]:
        """
        Get a registered environment method.

        Args:
            environment_name (str): Name of the environment
            method_name (str): Name of the method

        Returns:
            Optional[Callable]: The registered method or None if not found
        """
        return self.environments.get(environment_name, {}).get(method_name)

    def list_environments(self) -> Dict[str, list]:
        """
        List all registered environments and their methods.

        Returns:
            Dict[str, list]: Dictionary mapping environment names to lists of method names
        """
        return self.environments


# Global registry instance
environment_registry = EnvironmentRegistry()
