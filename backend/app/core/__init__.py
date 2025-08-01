"""
Core agent functionality integrated from computer-use-demo and agents.
"""

from .agent_loop import sampling_loop, APIProvider
from .tools import ToolVersion, ToolCollection, ToolResult
from .agent import Agent, ModelConfig, MessageHistory

__all__ = [
    "sampling_loop",
    "APIProvider", 
    "ToolVersion",
    "ToolCollection",
    "ToolResult",
    "Agent",
    "ModelConfig",
    "MessageHistory"
] 