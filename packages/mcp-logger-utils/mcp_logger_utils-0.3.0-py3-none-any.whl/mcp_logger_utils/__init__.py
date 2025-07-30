"""MCP Logger Utils - Shared utilities for MCP servers."""

try:
    from importlib.metadata import version
    __version__ = version("mcp-logger-utils")
except Exception:
    __version__ = "unknown"

from .json_utils import repair_and_parse_json
from .logger import MCPLogger, debug_tool
from .response_utils import create_success_response, create_error_response, create_response, parse_response
from .debug_tools import MCPDebugTools, create_debug_tools

__all__ = [
    "MCPLogger", 
    "debug_tool", 
    "repair_and_parse_json",
    "create_success_response",
    "create_error_response", 
    "create_response",
    "parse_response",
    "MCPDebugTools",
    "create_debug_tools"
]
