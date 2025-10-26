import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import yaml
from loguru import logger
from pydantic import BaseModel


class PhaseParametersConfig(BaseModel):
    """
    Configuration for MCTS phase parameters.
    """

    max_depth: int = 5
    max_iterations: int = 100
    performance_threshold: float = 0.4
    value_delta_threshold: float = 0.3
    convergence_checks: int = 5
    exploration_probability: float = 0.2
    num_nodes_per_iteration: int = 5
    task_timeout: float = 180.0  # task timeout in seconds (default: 3 minutes)
    node_selection_threshold: float = 0.5
    variations_per_concept: int = 5

    class Config:
        extra = "allow"  # allow additional phase-specific fields


class PhaseSearchParametersConfig(BaseModel):
    """
    Configuration for search parameters.
    """

    max_attempts: int = 3
    discount_factor: float = 0.9
    learning_rate: float = 0.9

    class Config:
        extra = "allow"  # allow additional phase-specific fields


class PhaseScoringParametersConfig(BaseModel):
    """
    Configuration for scoring parameters.
    """

    penalty_per_failure: int = 2
    penalty_per_error: int = 3
    penalty_per_attempt: int = 1
    fixed_by_problem_fixer_penalty: int = 5
    max_num_passed: int = 10

    class Config:
        extra = "allow"  # allow additional phase-specific fields


class PhaseEnvironmentConfig(BaseModel):
    """
    Configuration for phase environment.
    """

    name: str = "environment"

    class Config:
        extra = "allow"  # allow additional phase-specific fields


class PhaseConfig(BaseModel):
    """
    Configuration for MCTS phase.
    """

    phase_params: PhaseParametersConfig
    search_params: PhaseSearchParametersConfig
    scoring_params: PhaseScoringParametersConfig
    environment: PhaseEnvironmentConfig

    class Config:
        extra = "allow"  # allow additional phase-specific fields


class TreeConfig(BaseModel):
    """
    Configuration for tree initialization.
    """

    concepts: List[str]
    difficulties: List[str]

    class Config:
        extra = "allow"  # allow additional tree-specific fields


class ExperimentConfig(BaseModel):
    """
    Configuration for experiment.
    """

    name: str = "default"
    description: str = "Default experiment configuration"
    phase_sequences: Optional[List[str]] = ["phase_1", "phase_2", "phase_3"]

    class Config:
        extra = "allow"  # allow additional experiment-specific fields


class Settings(BaseModel):
    """
    Main application settings.
    """

    app_name: str = "PrismBench Search Interface"
    version: str = "0.1.0"
    debug: bool = False

    # service configurations
    tree_config: TreeConfig
    phase_configs: Dict[str, PhaseConfig]
    experiment_config: Optional[ExperimentConfig] = None

    # environment service
    env_service_url: str = "http://node-env:8000"

    class Config:
        extra = "allow"  # allow dynamic addition of custom phase configs


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Dictionary containing the configuration
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML config: {e}")

    if not isinstance(config, dict):
        raise ValueError(f"Config file {config_path} did not produce a dictionary.")

    logger.debug(f"Loaded config from {config_path}")
    return config


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    Loads from the tree and phase config files and creates Settings instance.

    Returns:
        Settings instance
    """
    # load the tree config
    tree_config_path = os.path.join("configs", "tree_configs.yaml")
    tree_config = load_yaml_config(tree_config_path)

    # load the phase config
    phase_config_path = os.path.join("configs", "phase_configs.yaml")
    phase_config = load_yaml_config(phase_config_path)

    # load the experiment config
    experiment_config_path = os.path.join("configs", "experiment_configs.yaml")
    experiment_config = load_yaml_config(experiment_config_path)

    # build phase configs dictionary - each phase gets all its parameters
    phase_configs = {}
    for phase_name, phase_data in phase_config.items():
        phase_configs[phase_name] = PhaseConfig(
            phase_params=PhaseParametersConfig(**phase_data["phase_params"] if "phase_params" in phase_data else {}),
            search_params=PhaseSearchParametersConfig(
                **phase_data["search_params"] if "search_params" in phase_data else {}
            ),
            scoring_params=PhaseScoringParametersConfig(
                **phase_data["scoring_params"] if "scoring_params" in phase_data else {}
            ),
            environment=PhaseEnvironmentConfig(**phase_data["environment"] if "environment" in phase_data else {}),
        )

    # create settings from the loaded configs
    settings = Settings(
        tree_config=TreeConfig(**tree_config["tree_configs"]),
        phase_configs=phase_configs,
        experiment_config=ExperimentConfig(**experiment_config),
    )

    logger.info(f"Initialized settings: {settings.app_name} v{settings.version}")
    return settings
