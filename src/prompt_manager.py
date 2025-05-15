from typing import Any, Dict, Optional

import yaml


class PromptManager:
    """
    A class that manages prompts and configurations for different roles.

    Args:
        config_file_path (str): The file path to the JSON/YML configuration file.
        Default is "src/agent_config_v4.json".

    Attributes:
        config_file_path (str): The file path to the JSON/YML configuration file.
        prompts (Dict[str, Dict[str, Any]]): A dictionary containing the loaded prompts.
    """

    def __init__(self, config_file_path: str = "src/agent_config_v4.json"):
        """
        Initializes a new instance of the PromptManager class.

        Args:
            config_file_path (str): The file path to the JSON/YML configuration file.
              Default is "src/agent_config_v3.json".
        """
        self.config_file_path = config_file_path
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self.load_prompts()

    def load_prompts(self):
        """
        Loads the prompts from the JSON configuration file.
        """

        with open(self.config_file_path, "r") as file:
            data = yaml.safe_load(file)
            self.prompts = data.get("prompts", {})

    def get_prompt_config(self, role: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the prompt configuration for the specified role.

        Args:
            role (str): The role for which to retrieve the prompt configuration.

        Returns:
            Optional[Dict[str, Any]]: The prompt configuration for the specified role, or None if not found.
        """

        return self.prompts.get(role)

    def get_prompt_template(self, role: str) -> Optional[str]:
        """
        Retrieves the prompt template for the specified role.

        Args:
            role (str): The role for which to retrieve the prompt template.

        Returns:
            Optional[str]: The prompt template for the specified role, or None if not found.
        """

        prompt_config = self.get_prompt_config(role)
        if prompt_config:
            return prompt_config["template"]
        return None

    def get_llm_config(self, role: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the LLM configuration for the specified role.

        Args:
            role (str): The role for which to retrieve the LLM configuration.

        Returns:
            Optional[Dict[str, Any]]: The LLM configuration for the specified role, or None if not found.
        """

        with open(self.config_file_path, "r") as file:
            data = yaml.safe_load(file)
            llms = data.get("llms", {})
            return llms.get(role)

    def get_interaction_template(self, role: str) -> Optional[str]:
        with open(self.config_file_path, "r") as file:
            data = yaml.safe_load(file)
            interactions = data["interaction_templates"][role]["templates"]
            return interactions

    def get_roles(self) -> list[str]:
        """
        Retrieves a list of roles for which prompts are available.

        Returns:
            list[str]: A list of roles for which prompts are available.
        """

        return list(self.prompts.keys())


# Usage example
if __name__ == "__main__":
    manager = PromptManager(config_file_path="src/agent_config_v6.yml")
    # Example: Get prompt configuration for a specific role
    writer_config = manager.get_prompt_config("writer")
    print("Writer prompt config:", writer_config)

    # Example: Get prompt template for a specific role
    analyst_template = manager.get_prompt_template("analyst")
    print("Analyst prompt template:", analyst_template)

    # Example: Get LLM configuration for a specific role
    writer_llm_config = manager.get_llm_config("writer")
    print("Writer LLM config:", writer_llm_config)

    # Example: Get all available roles
    roles = manager.get_roles()
    print("Available roles:", roles)
