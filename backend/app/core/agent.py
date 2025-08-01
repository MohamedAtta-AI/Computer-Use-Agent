"""
Integrated agent implementation with Claude API and computer use tools.
"""

import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from anthropic import Anthropic
from anthropic.types.beta import BetaMessageParam

from .agent_loop import sampling_loop, APIProvider
from .tools import ToolVersion, ToolCollection
from .utils.history_util import MessageHistory
from ..config import settings


@dataclass
class ModelConfig:
    """Configuration for the AI model."""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 1.0
    context_window_tokens: int = 180000


class Agent:
    """Integrated agent with computer use capabilities."""
    
    def __init__(
        self,
        model_config: Optional[ModelConfig] = None,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        self.model_config = model_config or ModelConfig()
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.system_prompt = system_prompt or ""
        self.history = MessageHistory()
        self.anthropic_client = Anthropic(
            api_key=self.api_key,
            extra_headers={"anthropic-beta": "code-execution-2025-05-22"}
        )
    
    async def process_message(
        self,
        message: str,
        progress_callback: Optional[callable] = None,
        tool_output_callback: Optional[callable] = None,
        api_response_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            message: The user's message
            progress_callback: Optional callback for streaming progress
            tool_output_callback: Optional callback for tool execution results
            api_response_callback: Optional callback for API responses
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Add user message to history
        self.history.add_message("user", message)
        
        # Convert history to Anthropic format
        messages = self._convert_history_to_anthropic_format()
        
        # Determine tool version based on model
        tool_version = self._get_tool_version(self.model_config.model)
        
        # Create callbacks
        def progress_handler(content_block):
            if progress_callback:
                progress_callback(content_block)
        
        def tool_handler(tool_result, tool_id):
            if tool_output_callback:
                tool_output_callback(tool_result, tool_id)
            # Add tool result to history
            self.history.add_tool_result(tool_id, tool_result)
        
        def api_handler(request, response, error):
            if api_response_callback:
                api_response_callback(request, response, error)
        
        # Run the sampling loop
        await sampling_loop(
            model=self.model_config.model,
            provider=APIProvider.ANTHROPIC,
            system_prompt_suffix=self.system_prompt,
            messages=messages,
            output_callback=progress_handler,
            tool_output_callback=tool_handler,
            api_response_callback=api_handler,
            api_key=self.api_key,
            max_tokens=self.model_config.max_tokens,
            tool_version=tool_version
        )
        
        # Get the latest assistant message
        latest_message = self.history.get_latest_assistant_message()
        
        return {
            "response": latest_message.content if latest_message else "",
            "tool_results": self.history.get_tool_results(),
            "message_count": len(self.history.messages)
        }
    
    def _convert_history_to_anthropic_format(self) -> List[BetaMessageParam]:
        """Convert message history to Anthropic API format."""
        messages = []
        
        for msg in self.history.messages:
            if msg.role == "user":
                messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif msg.role == "assistant":
                messages.append({
                    "role": "assistant", 
                    "content": msg.content
                })
            elif msg.role == "tool_result":
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.tool_id,
                        "content": msg.content,
                        "is_error": msg.is_error
                    }]
                })
        
        return messages
    
    def _get_tool_version(self, model_name: str) -> ToolVersion:
        """Determine tool version based on model name."""
        if "2025" in model_name:
            return ToolVersion.COMPUTER_USE_20250124
        else:
            return ToolVersion.COMPUTER_USE_20241022
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the message history."""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "tool_id": getattr(msg, 'tool_id', None),
                "is_error": getattr(msg, 'is_error', False)
            }
            for msg in self.history.messages
        ]
    
    def clear_history(self):
        """Clear the message history."""
        self.history.clear()
    
    def add_system_message(self, content: str):
        """Add a system message to the history."""
        self.history.add_message("system", content) 