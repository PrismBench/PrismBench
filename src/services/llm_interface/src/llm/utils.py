from typing import Any, Dict

import dspy
import yaml
from loguru import logger


def load_agent_config(config_file_path: str) -> Dict[str, Any]:
    """
    Loads the agent configuration from a YAML file.

    Args:
        config_file_path (str): The file path to the YAML configuration file.

    Returns:
        Dict[str, Any]: The agent configuration.
    """
    with open(config_file_path, "r") as file:
        agent_config = yaml.safe_load(file)

    # check if the the high level keys are present
    assert "role" in agent_config, "role is required for defining an agent"
    assert "model_name" in agent_config, "model_name is required for defining an agent"
    assert "model_provider" in agent_config, "model_provider is required for defining an agent"

    if "model_params" not in agent_config.keys():
        logger.warning(f"model_params is not defined for agent {agent_config['role']}, defaulting to empty dictionary")
        agent_config["model_params"] = {}

    assert "system_prompt" in agent_config, "system_prompt is required for defining an agent"
    assert "interaction_templates" in agent_config, "interaction_templates are required for defining an agent"
    assert "api_base" in agent_config, "api_base is required for defining an agent"

    # check if the interaction templates are a dictionary
    assert isinstance(agent_config["interaction_templates"], dict), "interaction_templates must be a dictionary"

    # check if the interaction templates have the required keys
    for interaction_template in agent_config["interaction_templates"].values():
        assert "inputs" in interaction_template.keys(), "inputs are required for defining an interaction template"
        assert "outputs" in interaction_template.keys(), "outputs are required for defining an interaction template"

        # check if the inputs have the required keys
        for input in interaction_template["inputs"]:
            assert "name" in input.keys(), "name is required for defining an input"
            assert "description" in input.keys(), "description is required for defining an input"
            if "type" not in input.keys():  # if type is not defined, default to str
                logger.warning(
                    f"type is not defined for agent {agent_config['name']}, interaction template {interaction_template['name']}, input {input['name']}, defaulting to str"
                )
                input["type"] = "str"

        # check if the outputs have the required keys
        for output in interaction_template["outputs"]:
            assert "name" in output.keys(), "name is required for defining an output"
            assert "description" in output.keys(), "description is required for defining an output"
            if "type" not in output.keys():  # if type is not defined, default to str
                logger.warning(
                    f"type is not defined for agent {agent_config['name']}, interaction template {interaction_template['name']}, output {output['name']}, defaulting to str"
                )
                output["type"] = "str"

    return agent_config


def make_agent_signature(agent_config: Dict[str, Any]) -> Dict[str, dspy.Signature]:
    """
    Makes a signature for an agent.

    Args:
        agent_config (Dict[str, Any]): The agent configuration.

    Returns:
        dspy.Signature: The signature for the agent.
    """
    # an agent can have multiple signatures. for now this only happens with the problem fixer since we might need ti to repair its own solution.
    agent_signatures = {}
    for interaction_template_name, interaction_template_details in agent_config["interaction_templates"].items():
        # https://dspy.ai/tutorials/conversation_history/
        attribute_dict = {"history": (dspy.History, dspy.InputField())}

        for interaction_input in interaction_template_details["inputs"]:
            attribute_dict[interaction_input["name"]] = (
                eval(interaction_input["type"]),
                dspy.InputField(description=interaction_input["description"]),
            )
        for interaction_output in interaction_template_details["outputs"]:
            attribute_dict[interaction_output["name"]] = (
                eval(interaction_output["type"]),
                dspy.OutputField(description=interaction_output["description"]),
            )

        signature = dspy.make_signature(signature=attribute_dict, instructions=agent_config["system_prompt"])
        agent_signatures[interaction_template_name] = dspy.Predict(signature)

    return agent_signatures


if __name__ == "__main__":
    import pprint

    agent_config = load_agent_config("/PrismBench/configs/agents/challenge_designer.yaml")
    pprint.pprint(agent_config)

    agent_signatures = make_agent_signature(agent_config)
    pprint.pprint(agent_signatures)
