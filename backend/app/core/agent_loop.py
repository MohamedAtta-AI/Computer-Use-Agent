"""
Agentic sampling loop that calls the Anthropic API and local implementation of anthropic-defined computer use tools.
"""

import platform
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

import httpx
from anthropic import (
    Anthropic,
    AnthropicBedrock,
    AnthropicVertex,
    APIError,
    APIResponseValidationError,
    APIStatusError,
)
from anthropic.types.beta import (
    BetaCacheControlEphemeralParam,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
    BetaToolUseBlockParam,
)

from .tools import (
    TOOL_GROUPS_BY_VERSION,
    ToolCollection,
    ToolResult,
    ToolVersion,
)

PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


# This system prompt is optimized for the Docker environment in this repository and
# specific tool combinations enabled.
# We encourage modifying this system prompt to ensure the model has context for the
# environment it is running in, and to provide any additional information that may be
# helpful for the task at hand.
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine using {platform.machine()} architecture with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* To open firefox, please just click on the firefox icon.  Note, firefox-esr is what is installed on your system.
* Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell. For example "(DISPLAY=:1 xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear. Take a screenshot to confirm it did.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_based_edit_tool or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {datetime.today().strftime('%A, %B %d, %Y')}.
</SYSTEM_CAPABILITY>

<IMPORTANT>
* When using Firefox, if a startup wizard appears, IGNORE IT.  Do not even click "skip this step".  Instead, click on the address bar where it says "Search or enter address", and enter the appropriate search term or URL there.
* If the item you are looking at is a pdf, if after taking a single screenshot of the pdf it seems that you want to read the entire document instead of trying to continue to read the pdf from your screenshots + navigation, determine the URL, use curl to download the pdf, install and use pdftotext to convert it to a text file, and then read that text file directly with your str_replace_based_edit_tool.
</IMPORTANT>"""


async def sampling_loop(
    *,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    output_callback: Callable[[BetaContentBlockParam], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    api_response_callback: Callable[
        [httpx.Request, httpx.Response | object | None, Exception | None], None
    ],
    api_key: str,
    only_n_most_recent_images: int | None = None,
    max_tokens: int = 4096,
    tool_version: ToolVersion,
    thinking_budget: int | None = None,
    token_efficient_tools_beta: bool = False,
):
    """
    Agentic sampling loop for the assistant/tool interaction of computer use.
    """
    tool_group = TOOL_GROUPS_BY_VERSION[tool_version]
    tool_collection = ToolCollection(*(ToolCls() for ToolCls in tool_group.tools))
    system = BetaTextBlockParam(
        type="text",
        text=f"{SYSTEM_PROMPT}{' ' + system_prompt_suffix if system_prompt_suffix else ''}",
    )

    while True:
        enable_prompt_caching = False
        betas = [tool_group.beta_flag] if tool_group.beta_flag else []
        
        if token_efficient_tools_beta:
            betas.append("token-efficient-tools-2025-01-24")
        
        if enable_prompt_caching:
            betas.append(PROMPT_CACHING_BETA_FLAG)
            _inject_prompt_caching(messages)

        # Filter messages to only include n most recent images if specified
        if only_n_most_recent_images is not None:
            messages = _maybe_filter_to_n_most_recent_images(
                messages, only_n_most_recent_images, min_removal_threshold=5
            )

        # Create the message to send to the API
        message_to_send = BetaMessageParam(
            role="user",
            content=[system] + messages,
        )

        # Make the API call
        try:
            if provider == APIProvider.ANTHROPIC:
                client = Anthropic(api_key=api_key, max_retries=4)
                response = await client.beta.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[message_to_send],
                    tools=tool_collection.to_params(),
                    beta_features=betas,
                    thinking_budget=thinking_budget,
                )
            elif provider == APIProvider.BEDROCK:
                client = AnthropicBedrock(api_key=api_key, max_retries=4)
                response = await client.beta.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[message_to_send],
                    tools=tool_collection.to_params(),
                    beta_features=betas,
                    thinking_budget=thinking_budget,
                )
            elif provider == APIProvider.VERTEX:
                client = AnthropicVertex(api_key=api_key, max_retries=4)
                response = await client.beta.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[message_to_send],
                    tools=tool_collection.to_params(),
                    beta_features=betas,
                    thinking_budget=thinking_budget,
                )
            else:
                raise ValueError(f"Unknown provider: {provider}")

            # Call the API response callback
            api_response_callback(
                httpx.Request("POST", "api_call"), response, None
            )

        except (APIError, APIResponseValidationError, APIStatusError) as e:
            api_response_callback(
                httpx.Request("POST", "api_call"), None, e
            )
            raise

        # Process the response
        response_params = _response_to_params(response)
        
        # Call the output callback for each content block
        for param in response_params:
            output_callback(param)

        # Check if the response contains tool use
        tool_use_blocks = [
            block for block in response.content
            if isinstance(block, BetaToolUseBlockParam)
        ]

        if not tool_use_blocks:
            # No tools used, we're done
            break

        # Execute tools and collect results
        for tool_use_block in tool_use_blocks:
            tool_name = tool_use_block.name
            tool_input = tool_use_block.input
            tool_use_id = tool_use_block.id

            try:
                # Execute the tool
                result = await tool_collection.execute_tool(tool_name, tool_input)
                
                # Call the tool output callback
                tool_output_callback(result, tool_use_id)
                
                # Create tool result block
                tool_result_block = _make_api_tool_result(result, tool_use_id)
                
                # Add the tool result to messages for the next iteration
                messages.append(tool_result_block)
                
            except Exception as e:
                # Handle tool execution errors
                error_result = ToolResult(
                    content=f"Error executing tool {tool_name}: {str(e)}",
                    is_error=True
                )
                tool_output_callback(error_result, tool_use_id)
                
                # Add error result to messages
                error_block = _make_api_tool_result(error_result, tool_use_id)
                messages.append(error_block)


def _maybe_filter_to_n_most_recent_images(
    messages: list[BetaMessageParam],
    images_to_keep: int,
    min_removal_threshold: int,
):
    """
    Filter messages to only include the n most recent images.
    """
    if len(messages) <= min_removal_threshold:
        return messages

    # Count images in messages
    image_count = 0
    for message in messages:
        if isinstance(message, dict) and "content" in message:
            for content in message["content"]:
                if isinstance(content, dict) and content.get("type") == "image":
                    image_count += 1
        elif hasattr(message, "content"):
            for content in message.content:
                if hasattr(content, "type") and content.type == "image":
                    image_count += 1

    if image_count <= images_to_keep:
        return messages

    # Remove oldest images until we have the desired number
    images_to_remove = image_count - images_to_keep
    removed_count = 0
    
    filtered_messages = []
    for message in messages:
        if removed_count >= images_to_remove:
            filtered_messages.append(message)
            continue
            
        if isinstance(message, dict) and "content" in message:
            filtered_content = []
            for content in message["content"]:
                if (isinstance(content, dict) and content.get("type") == "image" and 
                    removed_count < images_to_remove):
                    removed_count += 1
                else:
                    filtered_content.append(content)
            message["content"] = filtered_content
            filtered_messages.append(message)
        elif hasattr(message, "content"):
            filtered_content = []
            for content in message.content:
                if (hasattr(content, "type") and content.type == "image" and 
                    removed_count < images_to_remove):
                    removed_count += 1
                else:
                    filtered_content.append(content)
            message.content = filtered_content
            filtered_messages.append(message)
        else:
            filtered_messages.append(message)

    return filtered_messages


def _response_to_params(
    response: BetaMessage,
) -> list[BetaContentBlockParam]:
    """
    Convert response content blocks to parameters.
    """
    params = []
    for block in response.content:
        if isinstance(block, BetaTextBlock):
            params.append(BetaTextBlockParam(type="text", text=block.text))
        elif isinstance(block, BetaImageBlockParam):
            params.append(BetaImageBlockParam(
                type="image",
                source=block.source
            ))
        elif isinstance(block, BetaToolResultBlockParam):
            params.append(block)
    return params


def _inject_prompt_caching(
    messages: list[BetaMessageParam],
):
    """
    Inject prompt caching into messages.
    """
    # This is a placeholder for prompt caching functionality
    # Implementation would depend on specific caching requirements
    pass


def _make_api_tool_result(
    result: ToolResult, tool_use_id: str
) -> BetaToolResultBlockParam:
    """
    Convert a tool result to an API tool result block.
    """
    return BetaToolResultBlockParam(
        type="tool_result",
        tool_use_id=tool_use_id,
        content=result.content,
        is_error=result.is_error
    )


def _maybe_prepend_system_tool_result(result: ToolResult, result_text: str):
    """
    Maybe prepend system tool result to the result text.
    """
    if result.is_error:
        return f"Error: {result_text}"
    return result_text 