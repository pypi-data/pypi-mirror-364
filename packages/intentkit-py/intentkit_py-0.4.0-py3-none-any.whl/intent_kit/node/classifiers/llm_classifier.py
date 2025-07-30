"""
LLM-powered classifiers for intent-kit

This module provides LLM-powered classification functions that can be used
with ClassifierNode and HandlerNode.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from intent_kit.services.base_client import BaseLLMClient
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.utils.logger import Logger
from ..base import TreeNode

logger = Logger(__name__)

# Type alias for llm_config to support both dict and BaseLLMClient
LLMConfig = Union[Dict[str, Any], BaseLLMClient]


def create_llm_classifier(
    llm_config: Optional[LLMConfig],
    classification_prompt: str,
    node_descriptions: List[str],
) -> Callable[[str, List["TreeNode"], Optional[Dict[str, Any]]], Optional["TreeNode"]]:
    """
    Create an LLM-powered classifier function.

    Args:
        llm_config: (Optional) LLM configuration or client instance. If None, the builder or graph should inject a default.
        classification_prompt: Prompt template for classification
        node_descriptions: List of descriptions for each child node

    Returns:
        Classifier function that can be used with ClassifierNode
    """

    def llm_classifier(
        user_input: str,
        children: List["TreeNode"],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional["TreeNode"]:
        """
        LLM-powered classifier that determines which child node to execute.

        Args:
            user_input: User's input text
            children: List of available child nodes
            context: Optional context information to include in the prompt

        Returns:
            Selected child node or None if no match
        """
        logger.debug(f"LLM classifier input: {user_input}")
        if llm_config is None:
            raise ValueError(
                "No llm_config provided to LLM classifier. Please set a default on the graph or provide one at the node level."
            )
        try:
            # Build context information for the prompt
            context_info = ""
            if context:
                context_info = "\n\nAvailable Context Information:\n"
                for key, value in context.items():
                    context_info += f"- {key}: {value}\n"
                context_info += "\nUse this context information to help make more accurate classifications."

            # Build the classification prompt
            formatted_node_descriptions = "\n".join(
                [f"- {desc}" for desc in node_descriptions]
            )

            prompt = classification_prompt.format(
                user_input=user_input,
                node_descriptions=formatted_node_descriptions,
                context_info=context_info,
                num_nodes=len(children),
            )

            # Get LLM response
            if isinstance(llm_config, dict):
                # Obfuscate API key in debug log
                safe_config = llm_config.copy()
                if "api_key" in safe_config:
                    safe_config["api_key"] = "***OBFUSCATED***"
                logger.debug(f"LLM classifier config: {safe_config}")
                logger.debug(f"LLM classifier prompt: {prompt}")
                response = LLMFactory.generate_with_config(llm_config, prompt)
            else:
                # Use BaseLLMClient instance directly
                logger.debug(
                    f"LLM classifier using client: {type(llm_config).__name__}"
                )
                logger.debug(f"LLM classifier prompt: {prompt}")
                response = llm_config.generate(prompt)

            # Parse the response to get the selected node name
            selected_node_name = response.strip()
            logger.debug(f"LLM raw output: {response}")
            logger.debug(f"LLM classifier selected node: {selected_node_name}")

            # Find the child node with the matching name
            for child in children:
                if child.name == selected_node_name:
                    return child

            # If no exact match, try partial matching
            for child in children:
                if (
                    selected_node_name.lower() in child.name.lower()
                    or child.name.lower() in selected_node_name.lower()
                ):
                    return child

            # If still no match, return None
            logger.warning(f"No child node found matching '{selected_node_name}'")
            return None

        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return None

    return llm_classifier


def create_llm_arg_extractor(
    llm_config: LLMConfig, extraction_prompt: str, param_schema: Dict[str, Any]
) -> Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]]:
    """
    Create an LLM-powered argument extractor function.

    Args:
        llm_config: LLM configuration or client instance
        extraction_prompt: Prompt template for argument extraction
        param_schema: Parameter schema defining expected parameters

    Returns:
        Argument extractor function that can be used with HandlerNode
    """

    def llm_arg_extractor(
        user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        LLM-powered argument extractor that extracts parameters from user input.

        Args:
            user_input: User's input text
            context: Optional context information to include in the prompt

        Returns:
            Dictionary of extracted parameters
        """
        try:
            # Build context information for the prompt
            context_info = ""
            if context:
                context_info = "\n\nAvailable Context Information:\n"
                for key, value in context.items():
                    context_info += f"- {key}: {value}\n"
                context_info += "\nUse this context information to help extract more accurate parameters."

            # Build the extraction prompt
            logger.debug(f"LLM arg extractor param_schema: {param_schema}")
            logger.debug(
                f"LLM arg extractor param_schema types: {[(name, type(param_type)) for name, param_type in param_schema.items()]}"
            )

            param_descriptions = "\n".join(
                [
                    f"- {param_name}: {param_type.__name__ if hasattr(param_type, '__name__') else str(param_type)}"
                    for param_name, param_type in param_schema.items()
                ]
            )

            prompt = extraction_prompt.format(
                user_input=user_input,
                param_descriptions=param_descriptions,
                param_names=", ".join(param_schema.keys()),
                context_info=context_info,
            )

            # Get LLM response
            # Obfuscate API key in debug log
            if isinstance(llm_config, dict):
                safe_config = llm_config.copy()
                if "api_key" in safe_config:
                    safe_config["api_key"] = "***OBFUSCATED***"
                logger.debug(f"LLM arg extractor config: {safe_config}")
                logger.debug(f"LLM arg extractor prompt: {prompt}")
                response = LLMFactory.generate_with_config(llm_config, prompt)
            else:
                # Use BaseLLMClient instance directly
                logger.debug(
                    f"LLM arg extractor using client: {type(llm_config).__name__}"
                )
                logger.debug(f"LLM arg extractor prompt: {prompt}")
                response = llm_config.generate(prompt)

            # Parse the response to extract parameters
            # For now, we'll use a simple approach - in the future this could be JSON parsing
            extracted_params = {}

            # Simple parsing: look for "param_name: value" patterns
            lines = response.strip().split("\n")
            for line in lines:
                line = line.strip()
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        param_name = parts[0].strip()
                        param_value = parts[1].strip()
                        if param_name in param_schema:
                            extracted_params[param_name] = param_value

            logger.debug(f"Extracted parameters: {extracted_params}")
            return extracted_params

        except Exception as e:
            logger.error(f"LLM argument extraction failed: {e}")
            raise

    return llm_arg_extractor


def get_default_classification_prompt() -> str:
    """Get the default classification prompt template."""
    return """You are an intent classifier. Given a user input, select the most appropriate intent from the available options.

User Input: {user_input}

Available Intents:
{node_descriptions}

{context_info}

Instructions:
- Analyze the user input carefully
- Consider the available context information when making your decision
- Select the intent that best matches the user's request
- Return only the number (1-{num_nodes}) corresponding to your choice
- If no intent matches, return 0

Your choice (number only):"""


def get_default_extraction_prompt() -> str:
    """Get the default argument extraction prompt template."""
    return """You are a parameter extractor. Given a user input, extract the required parameters.

User Input: {user_input}

Required Parameters:
{param_descriptions}

{context_info}

Instructions:
- Extract the required parameters from the user input
- Consider the available context information to help with extraction
- Return each parameter on a new line in the format: "param_name: value"
- If a parameter is not found, use a reasonable default or empty string
- Be specific and accurate in your extraction

Extracted Parameters:
"""
