"""OpenAI API adapter implementation.

This module provides the OpenAI adapter that implements the APIAdapter interface
for converting between OpenAI and Anthropic API formats.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from collections.abc import AsyncIterator
from inspect import signature
from typing import Any, Literal, cast

import structlog

from ccproxy.core.interfaces import APIAdapter

from .models import (
    OpenAIChatCompletionRequest,
    OpenAIChatCompletionResponse,
    OpenAIChoice,
    OpenAIResponseMessage,
    OpenAIUsage,
    format_openai_tool_call,
    generate_openai_response_id,
    generate_openai_system_fingerprint,
)
from .streaming import OpenAIStreamProcessor


logger = structlog.get_logger(__name__)


# Model mapping from OpenAI to Claude
OPENAI_TO_CLAUDE_MODEL_MAPPING: dict[str, str] = {
    # GPT-4 models -> Claude 3.5 Sonnet (most comparable)
    "gpt-4": "claude-3-5-sonnet-20241022",
    "gpt-4-turbo": "claude-3-5-sonnet-20241022",
    "gpt-4-turbo-preview": "claude-3-5-sonnet-20241022",
    "gpt-4-1106-preview": "claude-3-5-sonnet-20241022",
    "gpt-4-0125-preview": "claude-3-5-sonnet-20241022",
    "gpt-4-turbo-2024-04-09": "claude-3-5-sonnet-20241022",
    "gpt-4o": "claude-3-7-sonnet-20250219",
    "gpt-4o-2024-05-13": "claude-3-7-sonnet-20250219",
    "gpt-4o-2024-08-06": "claude-3-7-sonnet-20250219",
    "gpt-4o-2024-11-20": "claude-3-7-sonnet-20250219",
    "gpt-4o-mini": "claude-3-5-haiku-latest",
    "gpt-4o-mini-2024-07-18": "claude-3-5-haiku-latest",
    # o1 models -> Claude models that support thinking
    "o1": "claude-opus-4-20250514",
    "o1-preview": "claude-opus-4-20250514",
    "o1-mini": "claude-sonnet-4-20250514",
    # o3 models -> Claude Opus 4
    "o3-mini": "claude-opus-4-20250514",
    # GPT-3.5 models -> Claude 3.5 Haiku (faster, cheaper)
    "gpt-3.5-turbo": "claude-3-5-haiku-20241022",
    "gpt-3.5-turbo-16k": "claude-3-5-haiku-20241022",
    "gpt-3.5-turbo-1106": "claude-3-5-haiku-20241022",
    "gpt-3.5-turbo-0125": "claude-3-5-haiku-20241022",
    # Generic fallback
    "text-davinci-003": "claude-3-5-sonnet-20241022",
    "text-davinci-002": "claude-3-5-sonnet-20241022",
}


def map_openai_model_to_claude(openai_model: str) -> str:
    """Map OpenAI model name to Claude model name.

    Args:
        openai_model: OpenAI model identifier

    Returns:
        Claude model identifier
    """
    # Direct mapping first
    claude_model = OPENAI_TO_CLAUDE_MODEL_MAPPING.get(openai_model)
    if claude_model:
        return claude_model

    # Pattern matching for versioned models
    if openai_model.startswith("gpt-4o-mini"):
        return "claude-3-5-haiku-latest"
    elif openai_model.startswith("gpt-4o") or openai_model.startswith("gpt-4"):
        return "claude-3-7-sonnet-20250219"
    elif openai_model.startswith("gpt-3.5"):
        return "claude-3-5-haiku-latest"
    elif openai_model.startswith("o1"):
        return "claude-sonnet-4-20250514"
    elif openai_model.startswith("o3"):
        return "claude-opus-4-20250514"
    elif openai_model.startswith("gpt"):
        return "claude-sonnet-4-20250514"

    # If it's already a Claude model, pass through unchanged
    if openai_model.startswith("claude-"):
        return openai_model

    # For unknown models, pass through unchanged we may change
    # this to a default model in the future
    return openai_model


class OpenAIAdapter(APIAdapter):
    """OpenAI API adapter for converting between OpenAI and Anthropic formats."""

    def __init__(self) -> None:
        """Initialize the OpenAI adapter."""
        pass

    def adapt_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Convert OpenAI request format to Anthropic format.

        Args:
            request: OpenAI format request

        Returns:
            Anthropic format request

        Raises:
            ValueError: If the request format is invalid or unsupported
        """
        try:
            # Parse OpenAI request
            openai_req = OpenAIChatCompletionRequest(**request)
        except Exception as e:
            raise ValueError(f"Invalid OpenAI request format: {e}") from e

        # Map OpenAI model to Claude model
        model = map_openai_model_to_claude(openai_req.model)

        # Convert messages
        messages, system_prompt = self._convert_messages_to_anthropic(
            openai_req.messages
        )

        # Build Anthropic request
        anthropic_request = {
            "model": model,
            "messages": messages,
            "max_tokens": openai_req.max_tokens or 4096,
        }

        # Add system prompt if present
        if system_prompt:
            anthropic_request["system"] = system_prompt

        # Add optional parameters
        if openai_req.temperature is not None:
            anthropic_request["temperature"] = openai_req.temperature

        if openai_req.top_p is not None:
            anthropic_request["top_p"] = openai_req.top_p

        if openai_req.stream is not None:
            anthropic_request["stream"] = openai_req.stream

        if openai_req.stop is not None:
            if isinstance(openai_req.stop, str):
                anthropic_request["stop_sequences"] = [openai_req.stop]
            else:
                anthropic_request["stop_sequences"] = openai_req.stop

        # Handle metadata - combine user field and metadata
        metadata = {}
        if openai_req.user:
            metadata["user_id"] = openai_req.user
        if openai_req.metadata:
            metadata.update(openai_req.metadata)
        if metadata:
            anthropic_request["metadata"] = metadata

        # Handle response format - add to system prompt for JSON mode
        if openai_req.response_format:
            format_type = (
                openai_req.response_format.type if openai_req.response_format else None
            )

            if format_type == "json_object" and system_prompt is not None:
                system_prompt += "\nYou must respond with valid JSON only."
                anthropic_request["system"] = system_prompt
            elif format_type == "json_schema" and system_prompt is not None:
                # For JSON schema, we can add more specific instructions
                if openai_req.response_format and hasattr(
                    openai_req.response_format, "json_schema"
                ):
                    system_prompt += f"\nYou must respond with valid JSON that conforms to this schema: {openai_req.response_format.json_schema}"
                anthropic_request["system"] = system_prompt

        # Handle reasoning_effort (o1 models) -> thinking configuration
        # Automatically enable thinking for o1 models even without explicit reasoning_effort
        if (
            openai_req.reasoning_effort
            or openai_req.model.startswith("o1")
            or openai_req.model.startswith("o3")
        ):
            # Map reasoning effort to thinking tokens
            thinking_tokens_map = {
                "low": 1000,
                "medium": 5000,
                "high": 10000,
            }

            # Default thinking tokens based on model if reasoning_effort not specified
            default_thinking_tokens = 5000  # medium by default
            if openai_req.model.startswith("o3"):
                default_thinking_tokens = 10000  # high for o3 models
            elif openai_req.model == "o1-mini":
                default_thinking_tokens = 3000  # lower for mini model

            thinking_tokens = (
                thinking_tokens_map.get(
                    openai_req.reasoning_effort, default_thinking_tokens
                )
                if openai_req.reasoning_effort
                else default_thinking_tokens
            )

            anthropic_request["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_tokens,
            }

            # Ensure max_tokens is greater than budget_tokens
            current_max_tokens = cast(int, anthropic_request.get("max_tokens", 4096))
            if current_max_tokens <= thinking_tokens:
                # Set max_tokens to be 2x thinking tokens + some buffer for response
                anthropic_request["max_tokens"] = thinking_tokens + max(
                    thinking_tokens, 4096
                )
                logger.debug(
                    "max_tokens_adjusted_for_thinking",
                    original_max_tokens=current_max_tokens,
                    thinking_tokens=thinking_tokens,
                    new_max_tokens=anthropic_request["max_tokens"],
                    operation="adapt_request",
                )

            # When thinking is enabled, temperature must be 1.0
            if (
                anthropic_request.get("temperature") is not None
                and anthropic_request["temperature"] != 1.0
            ):
                logger.debug(
                    "temperature_adjusted_for_thinking",
                    original_temperature=anthropic_request["temperature"],
                    new_temperature=1.0,
                    operation="adapt_request",
                )
                anthropic_request["temperature"] = 1.0
            elif "temperature" not in anthropic_request:
                # Set default temperature to 1.0 for thinking mode
                anthropic_request["temperature"] = 1.0

            logger.debug(
                "thinking_enabled",
                reasoning_effort=openai_req.reasoning_effort,
                model=openai_req.model,
                thinking_tokens=thinking_tokens,
                temperature=anthropic_request["temperature"],
                operation="adapt_request",
            )

        # Note: seed, logprobs, top_logprobs, and store don't have direct Anthropic equivalents
        if openai_req.seed is not None:
            logger.debug(
                "unsupported_parameter_ignored",
                parameter="seed",
                value=openai_req.seed,
                operation="adapt_request",
            )
        if openai_req.logprobs or openai_req.top_logprobs:
            logger.debug(
                "unsupported_parameters_ignored",
                parameters=["logprobs", "top_logprobs"],
                logprobs=openai_req.logprobs,
                top_logprobs=openai_req.top_logprobs,
                operation="adapt_request",
            )
        if openai_req.store:
            logger.debug(
                "unsupported_parameter_ignored",
                parameter="store",
                value=openai_req.store,
                operation="adapt_request",
            )

        # Handle tools/functions
        if openai_req.tools:
            anthropic_request["tools"] = self._convert_tools_to_anthropic(
                openai_req.tools
            )
        elif openai_req.functions:
            # Convert deprecated functions to tools
            anthropic_request["tools"] = self._convert_functions_to_anthropic(
                openai_req.functions
            )

        if openai_req.tool_choice:
            # Convert tool choice - can be string or OpenAIToolChoice object
            if isinstance(openai_req.tool_choice, str):
                anthropic_request["tool_choice"] = (
                    self._convert_tool_choice_to_anthropic(openai_req.tool_choice)
                )
            else:
                # Convert OpenAIToolChoice object to dict
                tool_choice_dict = {
                    "type": openai_req.tool_choice.type,
                    "function": openai_req.tool_choice.function,
                }
                anthropic_request["tool_choice"] = (
                    self._convert_tool_choice_to_anthropic(tool_choice_dict)
                )
        elif openai_req.function_call:
            # Convert deprecated function_call to tool_choice
            anthropic_request["tool_choice"] = self._convert_function_call_to_anthropic(
                openai_req.function_call
            )

        logger.debug(
            "format_conversion_completed",
            from_format="openai",
            to_format="anthropic",
            original_model=openai_req.model,
            anthropic_model=anthropic_request.get("model"),
            has_tools=bool(anthropic_request.get("tools")),
            has_system=bool(anthropic_request.get("system")),
            message_count=len(cast(list[Any], anthropic_request["messages"])),
            operation="adapt_request",
        )
        return anthropic_request

    def adapt_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Convert Anthropic response format to OpenAI format.

        Args:
            response: Anthropic format response

        Returns:
            OpenAI format response

        Raises:
            ValueError: If the response format is invalid or unsupported
        """
        try:
            # Extract original model from response metadata if available
            original_model = response.get("model", "gpt-4")

            # Generate response ID
            request_id = generate_openai_response_id()

            # Convert content
            content = ""
            tool_calls = []

            if "content" in response and response["content"]:
                for block in response["content"]:
                    if block.get("type") == "text":
                        content += block.get("text", "")
                    elif block.get("type") == "thinking":
                        # Handle thinking blocks - we can include them with a marker
                        thinking_text = block.get("thinking", "")
                        signature = block.get("signature")
                        if thinking_text:
                            content += f'<thinking signature="{signature}">{thinking_text}</thinking>'
                    elif block.get("type") == "tool_use":
                        tool_calls.append(format_openai_tool_call(block))
                    else:
                        logger.warning(
                            "unsupported_content_block_type", type=block.get("type")
                        )

            # Create OpenAI message
            # When there are tool calls but no content, use empty string instead of None
            # Otherwise, if content is empty string, convert to None
            final_content: str | None = content
            if tool_calls and not content:
                final_content = ""
            elif content == "":
                final_content = None

            message = OpenAIResponseMessage(
                role="assistant",
                content=final_content,
                tool_calls=tool_calls if tool_calls else None,
            )

            # Map stop reason
            finish_reason = self._convert_stop_reason_to_openai(
                response.get("stop_reason")
            )

            # Ensure finish_reason is a valid literal type
            if finish_reason not in ["stop", "length", "tool_calls", "content_filter"]:
                finish_reason = "stop"

            # Cast to proper literal type
            valid_finish_reason = cast(
                Literal["stop", "length", "tool_calls", "content_filter"], finish_reason
            )

            # Create choice
            choice = OpenAIChoice(
                index=0,
                message=message,
                finish_reason=valid_finish_reason,
                logprobs=None,  # Anthropic doesn't support logprobs
            )

            # Create usage
            usage_info = response.get("usage", {})
            usage = OpenAIUsage(
                prompt_tokens=usage_info.get("input_tokens", 0),
                completion_tokens=usage_info.get("output_tokens", 0),
                total_tokens=usage_info.get("input_tokens", 0)
                + usage_info.get("output_tokens", 0),
            )

            # Create OpenAI response
            openai_response = OpenAIChatCompletionResponse(
                id=request_id,
                object="chat.completion",
                created=int(time.time()),
                model=original_model,
                choices=[choice],
                usage=usage,
                system_fingerprint=generate_openai_system_fingerprint(),
            )

            logger.debug(
                "format_conversion_completed",
                from_format="anthropic",
                to_format="openai",
                response_id=request_id,
                original_model=original_model,
                finish_reason=valid_finish_reason,
                content_length=len(content) if content else 0,
                tool_calls_count=len(tool_calls),
                input_tokens=usage_info.get("input_tokens", 0),
                output_tokens=usage_info.get("output_tokens", 0),
                operation="adapt_response",
                choice=choice,
            )
            return openai_response.model_dump()

        except Exception as e:
            raise ValueError(f"Invalid Anthropic response format: {e}") from e

    async def adapt_stream(
        self, stream: AsyncIterator[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        """Convert Anthropic streaming response to OpenAI streaming format.

        Args:
            stream: Anthropic streaming response

        Yields:
            OpenAI format streaming chunks

        Raises:
            ValueError: If the stream format is invalid or unsupported
        """
        # Create stream processor
        processor = OpenAIStreamProcessor(
            enable_usage=True,
            enable_tool_calls=True,
            enable_text_chunking=False,  # Keep text as-is for compatibility
        )

        try:
            # Process the stream and parse SSE format back to dict objects
            async for sse_chunk in processor.process_stream(stream):
                if sse_chunk.startswith("data: "):
                    data_str = sse_chunk[6:].strip()
                    if data_str and data_str != "[DONE]":
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            logger.warning(
                                "streaming_chunk_parse_failed",
                                chunk_data=data_str[:100] + "..."
                                if len(data_str) > 100
                                else data_str,
                                operation="adapt_stream",
                            )
                            continue
        except Exception as e:
            raise ValueError(f"Error processing streaming response: {e}") from e

    def _convert_messages_to_anthropic(
        self, openai_messages: list[Any]
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Convert OpenAI messages to Anthropic format."""
        messages = []
        system_prompt = None

        for msg in openai_messages:
            if msg.role in ["system", "developer"]:
                # System and developer messages become system prompt
                if isinstance(msg.content, str):
                    if system_prompt:
                        system_prompt += "\n" + msg.content
                    else:
                        system_prompt = msg.content
                elif isinstance(msg.content, list):
                    # Extract text from content blocks
                    text_parts: list[str] = []
                    for block in msg.content:
                        if (
                            hasattr(block, "type")
                            and block.type == "text"
                            and hasattr(block, "text")
                            and block.text
                        ):
                            text_parts.append(block.text)
                    text_content = " ".join(text_parts)
                    if system_prompt:
                        system_prompt += "\n" + text_content
                    else:
                        system_prompt = text_content

            elif msg.role in ["user", "assistant"]:
                # Convert user/assistant messages
                anthropic_msg = {
                    "role": msg.role,
                    "content": self._convert_content_to_anthropic(msg.content),
                }

                # Add tool calls if present
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    # Ensure content is a list
                    if isinstance(anthropic_msg["content"], str):
                        anthropic_msg["content"] = [
                            {"type": "text", "text": anthropic_msg["content"]}
                        ]
                    if not isinstance(anthropic_msg["content"], list):
                        anthropic_msg["content"] = []

                    # Content is now guaranteed to be a list
                    content_list = anthropic_msg["content"]
                    for tool_call in msg.tool_calls:
                        content_list.append(
                            self._convert_tool_call_to_anthropic(tool_call)
                        )

                messages.append(anthropic_msg)

            elif msg.role == "tool":
                # Tool result messages
                if messages and messages[-1]["role"] == "user":
                    # Add to previous user message
                    if isinstance(messages[-1]["content"], str):
                        messages[-1]["content"] = [
                            {"type": "text", "text": messages[-1]["content"]}
                        ]

                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": getattr(msg, "tool_call_id", "unknown")
                        or "unknown",
                        "content": msg.content or "",
                    }
                    if isinstance(messages[-1]["content"], list):
                        messages[-1]["content"].append(tool_result)
                else:
                    # Create new user message with tool result
                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": getattr(msg, "tool_call_id", "unknown")
                        or "unknown",
                        "content": msg.content or "",
                    }
                    messages.append(
                        {
                            "role": "user",
                            "content": [tool_result],
                        }
                    )

        return messages, system_prompt

    def _convert_content_to_anthropic(
        self, content: str | list[Any] | None
    ) -> str | list[dict[str, Any]]:
        """Convert OpenAI content to Anthropic format."""
        if content is None:
            return ""

        if isinstance(content, str):
            # Check if the string contains thinking blocks
            thinking_pattern = r'<thinking signature="([^"]*)">(.*?)</thinking>'
            matches = re.findall(thinking_pattern, content, re.DOTALL)

            if matches:
                # Convert string with thinking blocks to list format
                anthropic_content: list[dict[str, Any]] = []
                last_end = 0

                for match in re.finditer(thinking_pattern, content, re.DOTALL):
                    # Add any text before the thinking block
                    if match.start() > last_end:
                        text_before = content[last_end : match.start()].strip()
                        if text_before:
                            anthropic_content.append(
                                {"type": "text", "text": text_before}
                            )

                    # Add the thinking block
                    signature = match.group(1)
                    thinking_text = match.group(2)
                    thinking_block: dict[str, Any] = {
                        "type": "thinking",
                        "thinking": thinking_text,  # Changed from "text" to "thinking"
                    }
                    if signature and signature != "None":
                        thinking_block["signature"] = signature
                    anthropic_content.append(thinking_block)

                    last_end = match.end()

                # Add any remaining text after the last thinking block
                if last_end < len(content):
                    remaining_text = content[last_end:].strip()
                    if remaining_text:
                        anthropic_content.append(
                            {"type": "text", "text": remaining_text}
                        )

                return anthropic_content
            else:
                return content

        # content must be a list at this point
        anthropic_content = []
        for block in content:
            # Handle both Pydantic objects and dicts
            if hasattr(block, "type"):
                # This is a Pydantic object
                block_type = getattr(block, "type", None)
                if (
                    block_type == "text"
                    and hasattr(block, "text")
                    and block.text is not None
                ):
                    anthropic_content.append(
                        {
                            "type": "text",
                            "text": block.text,
                        }
                    )
                elif (
                    block_type == "image_url"
                    and hasattr(block, "image_url")
                    and block.image_url is not None
                ):
                    # Get URL from image_url
                    if hasattr(block.image_url, "url"):
                        url = block.image_url.url
                    elif isinstance(block.image_url, dict):
                        url = block.image_url.get("url", "")
                    else:
                        url = ""

                    if url.startswith("data:"):
                        # Base64 encoded image
                        try:
                            media_type, data = url.split(";base64,")
                            media_type = media_type.split(":")[1]
                            anthropic_content.append(
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": data,
                                    },
                                }
                            )
                        except ValueError:
                            logger.warning(
                                "invalid_base64_image_url",
                                url=url[:100] + "..." if len(url) > 100 else url,
                                operation="convert_content_to_anthropic",
                            )
                    else:
                        # URL-based image (not directly supported by Anthropic)
                        anthropic_content.append(
                            {
                                "type": "text",
                                "text": f"[Image: {url}]",
                            }
                        )
            elif isinstance(block, dict):
                if block.get("type") == "text":
                    anthropic_content.append(
                        {
                            "type": "text",
                            "text": block.get("text", ""),
                        }
                    )
                elif block.get("type") == "image_url":
                    # Convert image URL to Anthropic format
                    image_url = block.get("image_url", {})
                    url = image_url.get("url", "")

                    if url.startswith("data:"):
                        # Base64 encoded image
                        try:
                            media_type, data = url.split(";base64,")
                            media_type = media_type.split(":")[1]
                            anthropic_content.append(
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": data,
                                    },
                                }
                            )
                        except ValueError:
                            logger.warning(
                                "invalid_base64_image_url",
                                url=url[:100] + "..." if len(url) > 100 else url,
                                operation="convert_content_to_anthropic",
                            )
                    else:
                        # URL-based image (not directly supported by Anthropic)
                        anthropic_content.append(
                            {
                                "type": "text",
                                "text": f"[Image: {url}]",
                            }
                        )

        return anthropic_content if anthropic_content else ""

    def _convert_tools_to_anthropic(
        self, tools: list[dict[str, Any]] | list[Any]
    ) -> list[dict[str, Any]]:
        """Convert OpenAI tools to Anthropic format."""
        anthropic_tools = []

        for tool in tools:
            # Handle both dict and Pydantic model cases
            if isinstance(tool, dict):
                if tool.get("type") == "function":
                    func = tool.get("function", {})
                    anthropic_tools.append(
                        {
                            "name": func.get("name", ""),
                            "description": func.get("description", ""),
                            "input_schema": func.get("parameters", {}),
                        }
                    )
            elif hasattr(tool, "type") and tool.type == "function":
                # Handle Pydantic OpenAITool model
                anthropic_tools.append(
                    {
                        "name": tool.function.name,
                        "description": tool.function.description or "",
                        "input_schema": tool.function.parameters,
                    }
                )

        return anthropic_tools

    def _convert_functions_to_anthropic(
        self, functions: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Convert OpenAI functions to Anthropic tools format."""
        anthropic_tools = []

        for func in functions:
            anthropic_tools.append(
                {
                    "name": func.get("name", ""),
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {}),
                }
            )

        return anthropic_tools

    def _convert_tool_choice_to_anthropic(
        self, tool_choice: str | dict[str, Any]
    ) -> dict[str, Any]:
        """Convert OpenAI tool_choice to Anthropic format."""
        if isinstance(tool_choice, str):
            mapping = {
                "none": {"type": "none"},
                "auto": {"type": "auto"},
                "required": {"type": "any"},
            }
            return mapping.get(tool_choice, {"type": "auto"})

        elif isinstance(tool_choice, dict) and tool_choice.get("type") == "function":
            func = tool_choice.get("function", {})
            return {
                "type": "tool",
                "name": func.get("name", ""),
            }

        return {"type": "auto"}

    def _convert_function_call_to_anthropic(
        self, function_call: str | dict[str, Any]
    ) -> dict[str, Any]:
        """Convert OpenAI function_call to Anthropic tool_choice format."""
        if isinstance(function_call, str):
            if function_call == "none":
                return {"type": "none"}
            elif function_call == "auto":
                return {"type": "auto"}

        elif isinstance(function_call, dict):
            return {
                "type": "tool",
                "name": function_call.get("name", ""),
            }

        return {"type": "auto"}

    def _convert_tool_call_to_anthropic(
        self, tool_call: dict[str, Any]
    ) -> dict[str, Any]:
        """Convert OpenAI tool call to Anthropic format."""
        func = tool_call.get("function", {})

        # Parse arguments string to dict for Anthropic format
        arguments_str = func.get("arguments", "{}")
        try:
            if isinstance(arguments_str, str):
                input_dict = json.loads(arguments_str)
            else:
                input_dict = arguments_str  # Already a dict
        except json.JSONDecodeError:
            logger.warning(
                "tool_arguments_parse_failed",
                arguments=arguments_str[:200] + "..."
                if len(str(arguments_str)) > 200
                else str(arguments_str),
                operation="convert_tool_call_to_anthropic",
            )
            input_dict = {}

        return {
            "type": "tool_use",
            "id": tool_call.get("id", ""),
            "name": func.get("name", ""),
            "input": input_dict,
        }

    def _convert_stop_reason_to_openai(self, stop_reason: str | None) -> str | None:
        """Convert Anthropic stop reason to OpenAI format."""
        if stop_reason is None:
            return None

        mapping = {
            "end_turn": "stop",
            "max_tokens": "length",
            "stop_sequence": "stop",
            "tool_use": "tool_calls",
            "pause_turn": "stop",
            "refusal": "content_filter",
        }

        return mapping.get(stop_reason, "stop")

    def adapt_error(self, error_body: dict[str, Any]) -> dict[str, Any]:
        """Convert Anthropic error format to OpenAI error format.

        Args:
            error_body: Anthropic error response

        Returns:
            OpenAI-formatted error response
        """
        # Extract error details from Anthropic format
        anthropic_error = error_body.get("error", {})
        error_type = anthropic_error.get("type", "internal_server_error")
        error_message = anthropic_error.get("message", "An error occurred")

        # Map Anthropic error types to OpenAI error types
        error_type_mapping = {
            "invalid_request_error": "invalid_request_error",
            "authentication_error": "invalid_request_error",
            "permission_error": "invalid_request_error",
            "not_found_error": "invalid_request_error",
            "rate_limit_error": "rate_limit_error",
            "internal_server_error": "internal_server_error",
            "overloaded_error": "server_error",
        }

        openai_error_type = error_type_mapping.get(error_type, "invalid_request_error")

        # Return OpenAI-formatted error
        return {
            "error": {
                "message": error_message,
                "type": openai_error_type,
                "code": error_type,  # Preserve original error type as code
            }
        }


__all__ = [
    "OpenAIAdapter",
    "OpenAIChatCompletionRequest",
    "OpenAIChatCompletionResponse",
    "map_openai_model_to_claude",
    "OPENAI_TO_CLAUDE_MODEL_MAPPING",
]
