from ..environment_client import EnvironmentClient
from ..mcts.base_phase import BasePhase
from ..tree import Tree


def create_phase(
    phase_name: str,
    tree: Tree,
    environment: EnvironmentClient,
    config: dict,
    **kwargs,
) -> BasePhase:
    """
    Create a BasePhase instance with a specific phase.

    Args:
        phase_name (str): Name of the phase to use
        tree (Tree): The search tree
        environment (EnvironmentClient): The environment client
        config (dict): Configuration dictionary
        **kwargs: Additional arguments passed to BasePhase

    Returns:
        BasePhase: Configured phase instance
    """
    return BasePhase(
        tree=tree,
        environment=environment,
        config=config,
        phase_name=phase_name,
        **kwargs,
    )
