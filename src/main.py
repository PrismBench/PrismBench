import os

from dotenv import load_dotenv
from loguru import logger
from datetime import datetime
from environment import CodingChallengeEnvironment, EnhancedCodingChallengeEnvironment
from mcts import MCTS, CompMCTS, ConceptMCTS
from tree import Tree
import yaml

load_dotenv()


def save_benchmark_params():

    timestamp = datetime.now().strftime("%m%d_%H%M")
    with open(
        os.path.join(
            os.getcwd(),
            "configs.yml",
        ),
        "r",
    ) as f:
        benchmark_configs = yaml.safe_load(f)

    with open(f"{timestamp}_params", "w") as f:
        yaml.dump(
            {
                "model_under_benchmark": {
                    "model": "Lllama3.1-405",
                    "version": "v7",
                    "timestamp": timestamp,
                },
                "environment": {
                    "phase 1 performance threshold": benchmark_configs["phase1"][
                        "performance_threshold"
                    ],
                    "phase 1 value threshold": benchmark_configs["phase1"][
                        "value_delta_threshold"
                    ],
                    "phase 1 exploration probability": benchmark_configs["phase1"][
                        "exploration_probability"
                    ],
                    "phase 2 value threshold": benchmark_configs["phase2"][
                        "value_delta_threshold"
                    ],
                    "phase 3 value threshold": benchmark_configs["phase3"][
                        "node_selection_threshold"
                    ],
                },
            },
            f,
            default_flow_style=False,
        )


if __name__ == "__main__":

    MAX_DEPTH = (
        5  # hard limit on the depth of the tree for phase 1, based on difficulty levels
    )
    ITERATIONS = 70  # number of iterations to run the MCTS (not used anymore)

    config_path = os.path.join(
        os.getcwd(),
        "agent_config_v7.yml",
    )
    save_benchmark_params()
    environment = CodingChallengeEnvironment(config_path=config_path)
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
    
    phase_one_agent = MCTS(
        environment,
        tree,
        max_depth=MAX_DEPTH,
        iterations=ITERATIONS,
    )
    phase_one_agent.run()
    logger.info("MCTS Phase 1 completed")

    phase_two_agent = ConceptMCTS(
        environment,
        phase_one_agent.tree,
        max_depth=MAX_DEPTH + 5,
        iterations=ITERATIONS,
    )
    # calculate the score for each node in the tree based on phase 2s scoring function
    for node in phase_two_agent.tree.nodes:
        if node.run_results:
            node.score = phase_two_agent.calculate_challenge_score(node.run_results[-1])
            phase_two_agent.backpropagate(node, node.score)

    phase_two_agent.run()
    logger.info("MCTS Phase 2 completed")

    phase_three_environment = EnhancedCodingChallengeEnvironment(
        config_path=config_path
    )
    pahse_three_agent = CompMCTS(
        phase_three_environment,
        phase_two_agent.tree,
    )
    pahse_three_agent.run()
    logger.info("MCTS Phase 3 completed")
