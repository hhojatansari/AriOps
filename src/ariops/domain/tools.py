"""Framework-independent contracts for bounded tool execution."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolDefinition:
    """Describes a tool available to an investigation workflow."""

    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None


@dataclass
class ToolCall:
    """Requests a named tool to run with structured arguments."""

    tool_name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    """Represents the outcome of a tool invocation."""

    tool_name: str
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class ToolExecutionError(Exception):
    """Raised when a requested tool cannot be executed."""

