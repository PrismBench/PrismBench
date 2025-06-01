import yaml


class PromptManager:
    """
    A class that manages prompts and configurations for an agent.

    Args:
        config_file_path (str): The file path to the JSON/YML configuration file.

    Attributes:
        config_file_path (str): The file path to the JSON/YML configuration file.
        name (str): The name of the agent.
        configs (Dict[str, Any]): The configurations for the agent.
        system_prompt (str): The system prompt for the agent.
        interaction_templates (List[Dict[str, Any]]): The interaction templates for the agent.
    """

    def __init__(self, config_file_path: str):
        """
        Initializes a new instance of the PromptManager class.

        Args:
            config_file_path (str): The file path to the JSON/YML configuration file.
        """
        self.config_file_path = config_file_path
        self.name = None
        self.configs = None
        self.system_prompt = None
        self.interaction_templates = None
        self.load_prompts()

    def load_prompts(self):
        """
        Loads the prompts from the JSON configuration file.
        """

        with open(self.config_file_path, "r") as file:
            agent_config = yaml.safe_load(file)
            self.name = agent_config["agent_name"]
            self.configs = agent_config["configs"]
            self.system_prompt = agent_config["system_prompt"]
            self.interaction_templates = agent_config["interaction_templates"]
        assert self.name is not None, "Agent name is required"
        assert self.configs is not None, "Agent configs are required"
        assert self.system_prompt is not None, "Agent system prompt is required"
        assert self.interaction_templates is not None, "Agent interaction templates are required"
        assert isinstance(self.configs, dict), "Agent configs must be a dictionary"
        assert isinstance(self.interaction_templates, list), "Agent interaction templates must be a list"
        temp = {}
        for template in self.interaction_templates:
            temp[template["name"]] = template
        self.interaction_templates = temp


# Usage example
if __name__ == "__main__":
    writer_manager = PromptManager(config_file_path="configs/agents/problem_solver.yml")
    # Example: Get prompt configuration for a specific role
    print("Agent (writer) name:", writer_manager.name)
    print("Agent (writer) configs:", writer_manager.configs)
    print("Agent (writer) system prompt:", writer_manager.system_prompt)
    print("Agent (writer) interaction templates:", writer_manager.interaction_templates)
