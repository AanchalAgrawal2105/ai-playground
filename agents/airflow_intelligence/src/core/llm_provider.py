"""
LLM Provider Abstraction Layer

This module provides a unified interface for different LLM providers:
- AWS Bedrock (boto3)
- Anthropic API (anthropic)
- OpenAI API (openai)
- Azure OpenAI

This allows the agent to work with any LLM provider without code changes.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All providers must implement the converse method for tool-enabled chat.
    """

    def __init__(
        self,
        model_id: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        """
        Initialize the LLM provider.

        Args:
            model_id: Model identifier (provider-specific)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def converse(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send a message and get a response (with optional tool use).

        Args:
            messages: Conversation history in provider format
            system: System prompt
            tools: Available tools in provider format

        Returns:
            Response dict with 'content', 'stop_reason', and optional 'tool_use'
        """
        pass

    @abstractmethod
    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format messages for the specific provider.

        Args:
            messages: Messages in standard format

        Returns:
            Messages in provider-specific format
        """
        pass

    @abstractmethod
    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format tools for the specific provider.

        Args:
            tools: Tools in standard format

        Returns:
            Tools in provider-specific format
        """
        pass


class AnthropicBedrockProvider(LLMProvider):
    """AWS Bedrock provider using boto3 (Claude models)."""

    def __init__(
        self,
        model_id: str,
        region: str = "us-east-1",
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        """
        Initialize Bedrock provider.

        Args:
            model_id: Bedrock model ID (e.g., "anthropic.claude-sonnet-4-...")
            region: AWS region
            aws_access_key: AWS access key (optional, uses IAM role if not provided)
            aws_secret_key: AWS secret key (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        """
        super().__init__(model_id, temperature, max_tokens)

        import boto3
        import os

        # Create Bedrock client
        # If AWS_PROFILE is set, use it to create a session (for SSO)
        # Otherwise, use explicit credentials or default credential chain
        aws_profile = os.getenv("AWS_PROFILE")

        if aws_profile:
            # Use AWS SSO profile
            session = boto3.Session(profile_name=aws_profile, region_name=region)
            self.bedrock = session.client("bedrock-runtime")
        elif aws_access_key and aws_secret_key:
            # Use explicit credentials
            self.bedrock = boto3.client(
                "bedrock-runtime",
                region_name=region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
            )
        else:
            # Use default credential chain (IAM role, env vars, etc.)
            self.bedrock = boto3.client("bedrock-runtime", region_name=region)
        logger.info(f"Initialized AWS Bedrock provider: {model_id} in {region}")

    def converse(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Call Bedrock Converse API."""
        request_params = {
            "modelId": self.model_id,
            "messages": messages,
            "system": [{"text": system}],
            "inferenceConfig": {
                "temperature": self.temperature,
                "maxTokens": self.max_tokens,
            },
        }

        if tools:
            request_params["toolConfig"] = {"tools": tools}

        try:
            response = self.bedrock.converse(**request_params)
            return response
        except Exception as e:
            logger.error(f"Bedrock API error: {e}")
            raise

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Bedrock uses standard message format."""
        return messages

    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Bedrock uses standard tool format."""
        return tools


class AnthropicAPIProvider(LLMProvider):
    """Anthropic API provider using anthropic SDK (Claude models)."""

    def __init__(
        self,
        model_id: str,
        api_key: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        """
        Initialize Anthropic API provider.

        Args:
            model_id: Model ID (e.g., "claude-sonnet-4-20250514")
            api_key: Anthropic API key
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        """
        super().__init__(model_id, temperature, max_tokens)

        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)
        logger.info(f"Initialized Anthropic API provider: {model_id}")

    def converse(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Call Anthropic Messages API."""
        request_params = {
            "model": self.model_id,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": system,
            "messages": self._convert_messages_to_anthropic(messages),
        }

        if tools:
            request_params["tools"] = tools

        try:
            response = self.client.messages.create(**request_params)

            # Convert Anthropic response to standard format
            return self._convert_anthropic_response(response)
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def _convert_messages_to_anthropic(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert standard messages to Anthropic format."""
        anthropic_messages = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", [])

            # Handle both list and dict content formats
            if isinstance(content, str):
                anthropic_messages.append({"role": role, "content": content})
            else:
                anthropic_messages.append({"role": role, "content": content})

        return anthropic_messages

    def _convert_anthropic_response(self, response: Any) -> Dict[str, Any]:
        """Convert Anthropic response to standard format."""
        return {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": response.content,
                }
            },
            "stopReason": response.stop_reason,
            "usage": {
                "inputTokens": response.usage.input_tokens,
                "outputTokens": response.usage.output_tokens,
                "totalTokens": response.usage.input_tokens
                + response.usage.output_tokens,
            },
        }

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Anthropic uses standard message format."""
        return messages

    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Anthropic uses standard tool format."""
        return tools


class OpenAIProvider(LLMProvider):
    """OpenAI API provider using openai SDK (GPT models)."""

    def __init__(
        self,
        model_id: str,
        api_key: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        """
        Initialize OpenAI API provider.

        Args:
            model_id: Model ID (e.g., "gpt-4-turbo", "gpt-4o")
            api_key: OpenAI API key
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        """
        super().__init__(model_id, temperature, max_tokens)

        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        logger.info(f"Initialized OpenAI API provider: {model_id}")

    def converse(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Call OpenAI Chat Completions API."""
        # Prepend system message
        openai_messages = [{"role": "system", "content": system}]
        openai_messages.extend(self._convert_messages_to_openai(messages))

        request_params = {
            "model": self.model_id,
            "messages": openai_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if tools:
            request_params["tools"] = self._convert_tools_to_openai(tools)
            request_params["tool_choice"] = "auto"

        try:
            response = self.client.chat.completions.create(**request_params)
            return self._convert_openai_response(response)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _convert_messages_to_openai(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert standard messages to OpenAI format."""
        openai_messages = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", [])

            # OpenAI expects text content as string
            if isinstance(content, list):
                text_parts = [
                    c.get("text", "") for c in content if c.get("type") == "text"
                ]
                content_str = " ".join(text_parts)
            else:
                content_str = str(content)

            openai_messages.append({"role": role, "content": content_str})

        return openai_messages

    def _convert_tools_to_openai(
        self, tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert standard tools to OpenAI format."""
        openai_tools = []

        for tool in tools:
            tool_spec = tool.get("toolSpec", {})
            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool_spec.get("name"),
                        "description": tool_spec.get("description"),
                        "parameters": tool_spec.get(
                            "inputSchema",
                            {"json": {"type": "object", "properties": {}}},
                        ).get("json", {"type": "object", "properties": {}}),
                    },
                }
            )

        return openai_tools

    def _convert_openai_response(self, response: Any) -> Dict[str, Any]:
        """Convert OpenAI response to standard format."""
        choice = response.choices[0]
        message = choice.message

        # Build content array
        content = []
        if message.content:
            content.append({"type": "text", "text": message.content})

        # Handle tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                content.append(
                    {
                        "type": "tool_use",
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "input": json.loads(tool_call.function.arguments),
                    }
                )

        # Determine stop reason
        stop_reason = "end_turn"
        if choice.finish_reason == "tool_calls":
            stop_reason = "tool_use"
        elif choice.finish_reason == "length":
            stop_reason = "max_tokens"

        return {
            "output": {
                "message": {
                    "role": "assistant",
                    "content": content,
                }
            },
            "stopReason": stop_reason,
            "usage": {
                "inputTokens": response.usage.prompt_tokens,
                "outputTokens": response.usage.completion_tokens,
                "totalTokens": response.usage.total_tokens,
            },
        }

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """OpenAI uses different message format."""
        return self._convert_messages_to_openai(messages)

    def format_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """OpenAI uses different tool format."""
        return self._convert_tools_to_openai(tools)


def create_llm_provider(
    provider_type: str,
    model_id: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    **kwargs,
) -> LLMProvider:
    """
    Factory function to create the appropriate LLM provider.

    Args:
        provider_type: Provider type ("bedrock", "anthropic", "openai")
        model_id: Model identifier
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        **kwargs: Provider-specific arguments

    Returns:
        LLMProvider instance

    Example:
        # AWS Bedrock
        provider = create_llm_provider(
            "bedrock",
            "anthropic.claude-sonnet-4-20250514-v1:0",
            region="us-east-1",
            aws_access_key="...",
            aws_secret_key="...",
        )

        # Anthropic API
        provider = create_llm_provider(
            "anthropic",
            "claude-sonnet-4-20250514",
            api_key="sk-ant-...",
        )

        # OpenAI
        provider = create_llm_provider(
            "openai",
            "gpt-4-turbo",
            api_key="sk-...",
        )
    """
    provider_type = provider_type.lower()

    if provider_type == "bedrock":
        return AnthropicBedrockProvider(
            model_id=model_id,
            region=kwargs.get("region", "us-east-1"),
            aws_access_key=kwargs.get("aws_access_key"),
            aws_secret_key=kwargs.get("aws_secret_key"),
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider_type == "anthropic":
        return AnthropicAPIProvider(
            model_id=model_id,
            api_key=kwargs["api_key"],
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif provider_type == "openai":
        return OpenAIProvider(
            model_id=model_id,
            api_key=kwargs["api_key"],
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Supported: bedrock, anthropic, openai"
        )
