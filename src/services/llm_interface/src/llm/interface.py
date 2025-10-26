import os
from typing import Any, Dict, List

import dspy
from loguru import logger

from .utils import load_agent_config, make_agent_signature


class LLMInterface(dspy.Module):
    def __init__(
        self,
        config_file_path: str,
        past_messages: List[Dict[str, Any]] | None = None,
    ) -> None:
        """
        Initialize the LLMInterface.

        Args:
            config_file_path: The path to the agent configuration file.
        """
        _agent_configs: Dict[str, Any] = load_agent_config(config_file_path)

        # set the agent's role, signatures, and interaction templates
        self.role: str = _agent_configs["role"]
        self.signatures: Dict[str, dspy.Predict] = make_agent_signature(_agent_configs)
        self.interaction_templates: Dict[str, List[str]] = {
            template_name: [input_var["name"] for input_var in template_configs["inputs"]]
            for template_name, template_configs in _agent_configs["interaction_templates"].items()
        }

        self.model_name: str = f"{_agent_configs['model_provider']}/{_agent_configs['model_name']}"
        self.model_params: Dict[str, Any] = _agent_configs["model_params"]
        self.api_base: str = _agent_configs["api_base"]

        # set the agent's history
        self.past_messages: List[Dict[str, Any]] = past_messages or []

        # set the agent's language model
        self.lm: dspy.LM = dspy.LM(
            model=self.model_name,
            **self.model_params,
            api_key=self.get_api_key(_agent_configs["model_provider"]),
            api_base=self.api_base,
            cache=False,
        )

    @staticmethod
    def get_api_key(model_provider: str) -> str:
        """
        Get the API key for the given model provider.

        Args:
            model_provider: The provider of the language model.

        Returns:
            The API key for the given model provider.
        """
        if model_provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif model_provider == "openrouter":
            return os.getenv("OPENROUTER_API_KEY")
        elif model_provider == "deepseek":
            return os.getenv("DEEPSEEK_API_KEY")
        elif model_provider == "togetherai":
            return os.getenv("TOGETHERAI_API_KEY")
        else:
            raise ValueError(f"Model provider {model_provider} not supported")

    async def interact(self, **kwargs) -> str:
        """
        Interact with the agent.

        Args:
            **kwargs: The input variables for the agent.

        Returns:
            (str): The output of the agent.
        """
        # check if the input variables match any of the interaction templates
        input_variables = kwargs.keys()

        for template_name, template_inputs in self.interaction_templates.items():
            if set(input_variables) == set(template_inputs):
                signature: dspy.Predict = self.signatures[template_name]
                break
        else:
            raise ValueError(f"No matching interaction template found for input variables: {input_variables}")

        # acutally send the damn thing
        try:
            output = await signature.acall(
                lm=self.lm,
                history=dspy.History(messages=self.past_messages),
                **kwargs,
            )
            self.past_messages.append({**kwargs, **output})
            logger.info(
                f"Successfully interacted with --{self.role}-- using the --{template_name}-- template with the following inputs: {kwargs}"
            )
        except Exception as e:
            logger.opt(exception=e).error(
                f"Error interacting with --{self.role}-- using the --{template_name}-- template with the following inputs: {kwargs}"
            )
            raise e

        return output.response

    def get_past_messages(self) -> List[Dict[str, Any]]:
        """
        Get the past messages.

        Returns:
            (List[Dict[str, Any]]): The past messages.
        """
        return self.past_messages
