import asyncio

from src.environment_client import EnvironmentClient
from src.mcts.utils import create_phase
from src.mcts.phase_registry import phase_registry
from src.tree import Tree

# Load all phase modules to register their strategies
phase_registry.load_phase_modules()

tree = Tree(
    concepts=[
        "loops",
        "conditionals",
        "functions",
        "data_structures",
        "algorithms",
        "error_handling",
        "recursion",
        "sorting",
        "searching",
        "dynamic_programming",
    ],
    difficulties=[
        "very easy",
        "easy",
        "medium",
        "hard",
        "very hard",
    ],
)
tree.initialize_tree()

# Create environment client with required config
environment_config = {"base_url": "http://node-env:8000"}
environment = EnvironmentClient(environment_config)

config_phase_1 = {
    "phase_params": {
        "performance_threshold": 0.4,
        "value_delta_threshold": 0.3,
        "convergence_checks": 10,
        "max_depth": 3,
        "max_iterations": 10,
        "exploration_probability": 0.2,
        "num_nodes_per_iteration": 5,
    },
    "search_params": {
        "max_attempts": 3,
        "discount_factor": 0.9,
        "learning_rate": 0.9,
    },
    "scoring_params": {
        "penalty_per_failure": 2,
        "penalty_per_error": 3,
        "penalty_per_attempt": 1,
        "fixed_by_problem_fixer_penalty": 5,
        "max_num_passed": 10,
    },
}
config_phase_2 = {
    "phase_params": {
        "performance_threshold": 0.4,
        "value_delta_threshold": 0.2,
        "convergence_checks": 10,
        "max_depth": 10,
        "max_iterations": 10,
        "exploration_probability": 0.2,
        "exploration_weight": 1.414,
        "challenge_threshold": 0.5,
        "num_nodes_per_iteration": 5,
    },
    "search_params": {
        "max_attempts": 3,
        "discount_factor": 0.9,
        "learning_rate": 0.9,
    },
    "scoring_params": {
        "penalty_per_failure": 2,
        "penalty_per_error": 3,
        "penalty_per_attempt": 1,
        "fixed_by_problem_fixer_penalty": 5,
        "max_num_passed": 10,
    },
}
config_phase_3 = {
    "phase_params": {
        "performance_threshold": 0.4,
        "value_delta_threshold": 0.2,
        "convergence_checks": 10,
        "max_depth": 10,
        "max_iterations": 70,
        "exploration_probability": 0.2,
        "exploration_weight": 1.414,
        "challenge_threshold": 0.5,
        "num_nodes_per_iteration": 5,
        "node_selection_threshold": 0.0,
        "variations_per_concept": 5,
    },
    "search_params": {
        "max_attempts": 5,
        "discount_factor": 0.9,
        "learning_rate": 0.9,
    },
    "scoring_params": {
        "penalty_per_failure": 2,
        "penalty_per_error": 3,
        "penalty_per_attempt": 1,
        "fixed_by_problem_fixer_penalty": 5,
        "max_num_passed": 10,
    },
}

if __name__ == "__main__":

    async def main() -> None:
        phase_one = create_phase(
            phase_name="phase_1",
            tree=tree,
            environment=environment,
            config=config_phase_1,
        )

        await phase_one.run()

        phase_two = create_phase(
            phase_name="phase_2",
            tree=phase_one.tree,
            environment=environment,
            config=config_phase_2,
        )

        await phase_two.run()

        phase_three = create_phase(
            phase_name="phase_3",
            tree=phase_two.tree,
            environment=environment,
            config=config_phase_3,
        )

        await phase_three.run()

    asyncio.run(main())
