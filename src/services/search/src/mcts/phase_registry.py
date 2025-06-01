import importlib
from pathlib import Path
from typing import Callable, Dict, List, Optional

from loguru import logger


class PhaseRegistry:
    """
    Registry for phase strategies using decorators.

    This class is used to register and manage phase strategies.
    It automatically discovers and loads phase modules from the phases directory.
    """

    def __init__(self) -> None:
        """Initialize the registry with empty phase collections."""
        self.phases: Dict[str, Dict[str, Callable]] = {}
        self._loaded_modules: List[str] = []

    def load_phase_modules(
        self,
        phases_directory: Optional[str] = None,
    ) -> List[str]:
        """
        Automatically import all discovered phase modules to register phases.

        Args:
            phases_directory: Optional custom directory for phase modules

        Returns:
            List of loaded phase module names
        """
        discovered_phases = self.discover_phases(phases_directory)
        loaded_phases = []

        for phase_module in discovered_phases:
            if phase_module not in self._loaded_modules:
                try:
                    # import the module to trigger phase registration
                    importlib.import_module(f"..{phase_module}", package=__name__)
                    loaded_phases.append(phase_module)
                    self._loaded_modules.append(phase_module)
                    logger.debug(f"Loaded phase module: {phase_module}")
                except ImportError as e:
                    logger.error(f"Failed to load phase module {phase_module}: {e}")

        logger.info(f"Successfully loaded {len(loaded_phases)} phase modules")
        logger.info(f"Available phases: {self.phases}")
        return loaded_phases

    def discover_phases(
        self,
        phases_directory: Optional[str] = None,
    ) -> List[str]:
        """
        Discover all phase modules in the phases directory.

        Args:
            phases_directory: Optional custom directory for phase modules.
                                Defaults to the directory containing this file.

        Returns:
            List of discovered phase module names
        """
        if phases_directory is None:
            # default to the directory containing this file
            phases_dir = Path(__file__).parent
        else:
            phases_dir = Path(phases_directory)

        discovered_phases = []

        # look for phase_*.py files
        for file_path in phases_dir.glob("phase_*.py"):
            if "phase_registry.py" in file_path.name:
                continue
            if file_path.is_file() and not file_path.name.startswith("__"):
                module_name = file_path.stem
                discovered_phases.append(module_name)

        logger.info(f"Discovered phases: {discovered_phases}")
        return discovered_phases

    def register_phase_method(
        self,
        phase_name: str,
        method_name: str,
    ) -> Callable:
        """
        Decorator to register a phase method.

        Args:
            phase_name (str): Name of the phase (e.g., 'phase_1', 'phase_2')
            method_name (str): Name of the method being registered (e.g., 'select_node', 'expand_node')

        Returns:
            Callable: The decorator function
        """

        def decorator(func: Callable) -> Callable:
            if phase_name not in self.phases:
                self.phases[phase_name] = {}
            self.phases[phase_name][method_name] = func
            logger.debug(f"Registered {method_name} for phase {phase_name}")
            return func

        return decorator

    def get_phase_method(
        self,
        phase_name: str,
        method_name: str,
    ) -> Optional[Callable]:
        """
        Get a registered phase method.

        Args:
            phase_name (str): Name of the phase
            method_name (str): Name of the method

        Returns:
            Optional[Callable]: The registered method or None if not found
        """
        return self.phases.get(phase_name, {}).get(method_name)

    def list_phases(self) -> Dict[str, Dict[str, Callable]]:
        """
        List all registered phases and their methods.

        Returns:
            Dict[str, list]: Dictionary mapping phase names to lists of method names
        """
        return self.phases


# global phase registry instance
phase_registry = PhaseRegistry()
