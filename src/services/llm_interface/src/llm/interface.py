import os
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool, tool
from langchain_openai import ChatOpenAI
from loguru import logger

from .prompt_manager import PromptManager


def extract_content_from_text(
    text: str,
    start_delimiter: str,
    end_delimiter: str,
) -> str:
    """
    Extract content between two delimiters from text.

    Args:
        text (str): The text to extract content from
        start_delimiter (str): The starting delimiter
        end_delimiter (str): The ending delimiter

    Returns:
        str: The extracted content, or None if not found
    """
    try:
        pattern = f"{start_delimiter}(.*?){end_delimiter}"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
    except Exception as e:
        logger.error(f"Error extracting content: {e}")
    return None


class LLMInterface:
    """
    LLMInterface provides a unified interface for interacting with various language models.

    This class simplifies the process of working with different LLM providers and supports
    both simple chat interactions and agentic workflows through Langchain.

    Attributes:
        prompt_manager (PromptManager): Manages prompts and configurations.
        providers (Dict[str, ProviderConfig]): API configurations for different providers.
        role (Optional[str]): Currently active role for the LLM.
        llm (Optional[BaseChatModel]): The active LLM instance.
        system_prompt (Optional[str]): System prompt for the current role.
        interaction_templates (Optional[List[Dict[str, Any]]]): Templates for interactions.
        conversation_history (List[BaseMessage]): History of the conversation.
        verbose (bool): Whether to enable verbose logging.
        available_tools (List[BaseTool]): Tools available for agent use.
        config_file (str): Path to the YAML configuration file.
    """

    def __init__(
        self,
        prompt_manager: PromptManager,
        providers: Dict[str, Dict[str, str]],
        verbose: bool = False,
    ) -> None:
        """
        Initialize the LLMInterface with injected dependencies.

        Args:
            prompt_manager (PromptManager): Prompt configuration manager.
            providers (Dict[str, Dict[str, str]]): Provider API and URL configurations.
            verbose (bool): Enable verbose logging. Defaults to False.
        """
        self.prompt_manager = prompt_manager
        self.role: Optional[str] = prompt_manager.name
        self.configs: Optional[Dict[str, Any]] = prompt_manager.configs
        self.system_prompt: Optional[str] = prompt_manager.system_prompt
        self.interaction_templates: Optional[Dict[str, Any]] = prompt_manager.interaction_templates

        self.providers = providers
        self.model: Optional[BaseChatModel] = None
        self.conversation_history: List[BaseMessage] = []
        self.available_tools: List[BaseTool] = []
        self.verbose = verbose

        self.set_role()

    def set_role(self) -> bool:
        """
        Set the current role and configure the LLM accordingly.

        Returns:
            bool: True if role was set successfully, False otherwise.
        """

        # Set up callbacks for verbose mode
        callbacks = [StdOutCallbackHandler()] if self.verbose else None

        # Create the appropriate LLM based on provider
        try:
            self.model = self._create_llm_instance(callbacks)
            if self.model:
                # Reset conversation history when changing roles
                self.conversation_history = []
                logger.info(f"Model '{self.configs.get('model_name')}' loaded for role '{self.role}'")
                return True
            return False
        except Exception as e:
            logger.exception(f"Failed to initialize LLM for role '{self.role}': {e}")
            return False

    def _create_llm_instance(
        self,
        callbacks: Optional[List[Any]] = None,
    ) -> Optional[BaseChatModel]:
        """
        Create an LLM instance based on the provided configuration.

        Args:
            callbacks (Optional[List[Any]]): Callbacks for the LLM.

        Returns:
            Optional[BaseChatModel]: The created LLM instance or None if creation failed.
        """
        provider = self.configs.get("provider", "openai").lower()
        model_name = self.configs.get("model_name", "")
        params = self.configs.get("params", {})

        try:
            # Build model parameters including API details if provided
            model_params = params.copy()
            provider_config = self.providers.get(provider)

            # Handle different providers
            if not provider_config:
                logger.error(f"Configuration not found for provider '{provider}'")
                return None

            # Handle OpenAI-compatible providers (OpenAI, DeepSeek, TogetherAI, Local)
            if provider in ["openai", "deepseek", "togetherai", "local"]:
                api_key = provider_config.get("api_key")
                base_url = provider_config.get("base_url")

                if not api_key:
                    logger.error(f"API key not found for provider '{provider}' in configuration.")
                    return None
                if not base_url:
                    logger.error(f"Base URL not found for provider '{provider}' in configuration.")
                    return None

                model_params["api_key"] = api_key
                model_params["base_url"] = base_url

                return ChatOpenAI(model=model_name, callbacks=callbacks, **model_params)

            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY", "")
                if not api_key:
                    logger.error("ANTHROPIC_API_KEY not found in environment variables for provider 'anthropic'")
                    return None

                model_params["api_key"] = api_key
                return ChatAnthropic(model_name=model_name, callbacks=callbacks, **model_params)

            else:
                logger.error(f"Unsupported provider: '{provider}'")
                return None

        except Exception as e:
            logger.exception(f"Error creating LLM instance: {e}")
            return None

    def _format_input(self, **kwargs) -> Optional[str]:
        """
        Format input using the appropriate interaction template.

        Args:
            **kwargs: Keyword arguments for template formatting.

        Returns:
            Optional[Tuple[str, str]]: Template name and formatted input string or None if formatting failed.
        """
        templates = self.interaction_templates
        if not templates:
            # If no templates are defined, combine all kwargs into a single string
            return "basic", "\n".join([f"{k}: {v}" for k, v in kwargs.items()])

        # Try to find a matching template
        for template in templates:
            required_keys = templates[template].get("required_keys", [])
            if all(key in kwargs for key in required_keys):
                template_str = templates[template].get("template", "")
                try:
                    return template, template_str.format(**kwargs)
                except KeyError as e:
                    logger.error(f"Error formatting template: {e}")

        # No matching template found
        logger.warning(f"No matching template found for keys: {list(kwargs.keys())}")
        return None, None

    def _format_output(self, template_name: str, response: str) -> Optional[str]:
        """
        Format the output using the appropriate output parser.

        Args:
            template_name (str): The name of the template used.
            response (str): The response from the LLM.

        Returns:
            Optional[str]: The formatted output string or None if formatting failed.
        """
        output_format = self.interaction_templates[template_name].get("output_format", {})
        try:
            formatted_output = extract_content_from_text(
                response,
                output_format.get("response_begin", ""),
                output_format.get("response_end", ""),
            )
            return formatted_output
        except Exception as e:
            logger.exception(f"Error formatting output: {e}")
            return None

    def interact(self, **kwargs) -> Optional[str]:
        """
        Interact with the LLM using the current role and configuration.

        Args:
            **kwargs: Keyword arguments used for formatting the input.

        Returns:
            Optional[str]: The LLM's response, or None if an error occurred.
        """
        if not self.model or not self.system_prompt:
            logger.error("LLM or system prompt not configured")
            return None

        try:
            # Format the input using templates
            template_name, input_text = self._format_input(**kwargs)
            if not input_text:
                logger.error("Failed to format input")
                return None

            # Construct the messages
            messages = (
                [SystemMessage(content=self.system_prompt)]
                + self.conversation_history
                + [HumanMessage(content=input_text)]
            )

            if self.verbose:
                logger.info("\n--- Sending to LLM ---")
                for msg in messages:
                    logger.info(f"{msg.type}: {msg.content}")

            # Get response from the LLM
            ai_message = self.model.invoke(messages)

            if self.verbose:
                logger.info("\n--- Received from LLM ---")
                logger.info(f"{ai_message.type}: {ai_message.content}")

            # Update conversation history
            self.conversation_history.append(HumanMessage(content=input_text))
            self.conversation_history.append(ai_message)

            formatted_output = self._format_output(template_name, ai_message.content)
            if not formatted_output:
                logger.error("Formatted output is empty")
                return None

            return formatted_output
        except Exception as e:
            logger.exception(f"Error interacting with LLM: {e}")
            return None

    def register_tools(self, tools: List[BaseTool]) -> None:
        """
        Register tools for use with agent workflows.

        Args:
            tools (List[BaseTool]): List of tools to register.
        """
        self.available_tools.extend(tools)
        logger.info(f"Registered {len(tools)} tools: {[tool.name for tool in tools]}")

    def create_agent(self) -> Optional[Runnable]:
        """
        Create an agent with the current LLM and registered tools.

        Returns:
            Optional[Runnable]: A Langchain Runnable agent or None if creation failed.
        """
        if not self.model or not self.system_prompt:
            logger.error("LLM or system prompt not configured")
            return None

        if not self.available_tools:
            logger.warning("No tools available for agent")

        try:
            # Create prompt template with tool descriptions
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

            # Create agent chain
            agent = (
                {
                    "input": lambda x: x["input"],
                    "chat_history": lambda x: x.get("chat_history", []),
                    "agent_scratchpad": lambda x: x.get("intermediate_steps", []),
                }
                | prompt
                | self.model
                | StrOutputParser()
            )

            return agent
        except Exception as e:
            logger.exception(f"Error creating agent: {e}")
            return None

    def run_agent(
        self,
        input_text: str,
        history: Optional[List[BaseMessage]] = None,
    ) -> str:
        """
        Run the agent with the given input.

        Args:
            input_text (str): Input text for the agent.
            history (Optional[List[BaseMessage]]): Optional conversation history.

        Returns:
            str: The agent's response.
        """
        agent = self.create_agent()
        if not agent:
            return "Failed to create agent"

        history = history or self.conversation_history

        try:
            response = agent.invoke({"input": input_text, "chat_history": history, "intermediate_steps": []})

            # Update conversation history
            self.conversation_history.append(HumanMessage(content=input_text))
            self.conversation_history.append(AIMessage(content=response))

            return response
        except Exception as e:
            logger.exception(f"Error running agent: {e}")
            return f"Agent execution failed: {str(e)}"

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Retrieve the conversation history.

        Returns:
            List[Dict[str, str]]: A list of dictionaries representing the conversation history.
            Each dictionary contains 'role' (either 'human' or 'ai') and 'content' keys.
        """
        result = []
        for msg in self.conversation_history:
            content = msg.content if hasattr(msg, "content") else str(msg)
            role = "human" if isinstance(msg, HumanMessage) else "ai"
            result.append({"role": role, "content": content})
        return result

    def clear_memory(self) -> None:
        """
        Clear the conversation history.
        """
        self.conversation_history = []
        logger.info("Conversation history cleared.")

    @classmethod
    def from_config_file(
        cls,
        config_file_path: str,
        verbose: bool = False,
    ) -> "LLMInterface":
        """
        Factory to create LLMInterface from a config file path.
        """
        # Load API keys from .env file
        load_dotenv("apis.key")
        prompt_manager = PromptManager(config_file_path)
        providers = cls._initialize_providers()
        return cls(prompt_manager=prompt_manager, providers=providers, verbose=verbose)

    @staticmethod
    def _initialize_providers() -> Dict[str, Dict[str, str]]:
        """
        Initialize configurations for different LLM providers.

        Returns:
            Dict[str, ProviderConfig]: Dictionary of provider configurations.
        """
        # Load environment variables for API keys
        load_dotenv("apis.key")

        return {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            },
            "deepseek": {
                "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            },
            "togetherai": {
                "api_key": os.getenv("TOGETHERAI_API_KEY", ""),
                "base_url": os.getenv("TOGETHERAI_BASE_URL", "https://api.together.xyz/v1"),
            },
            "local": {
                "api_key": "local_key",  # Not needed for local models
                "base_url": os.getenv("LOCAL_AI_BASE_URL", "http://localhost:1234/v1"),
            },
        }


# Example tool definition for use with agents
@tool
def calculator(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error calculating: {str(e)}"


# Usage example
if __name__ == "__main__":
    # Initialize the LLMInterface with the configuration file
    config_file_path = "configs/agents/challenge_designer.yml"
    agent = LLMInterface.from_config_file(config_file_path, verbose=True)

    # Example: Using simple chat interface
    response = agent.interact(concepts="binary search", difficulty_level="easy")
    logger.info(f"Response: {response}")

    # Example: Using agent capabilities
    response = agent.interact(concepts="binary search", difficulty_level="easy")
    logger.info(f"Response: {response}")

    # Run the agent
    response = agent.run_agent("Calculate 123 * 456 and use the result to write a short story")
    logger.info(f"Agent response: {response}")
