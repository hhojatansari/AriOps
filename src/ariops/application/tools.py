"""In-memory registry for bounded tool execution."""

from collections.abc import Callable
from typing import Any, TypeAlias

from ariops.domain.tools import (
    ToolCall,
    ToolDefinition,
    ToolExecutionError,
    ToolResult,
)

ToolHandler: TypeAlias = Callable[[dict[str, Any]], dict[str, Any]]


class ToolRegistry:
    """Register and execute named tool handlers."""

    def __init__(self) -> None:
        self._definitions: dict[str, ToolDefinition] = {}
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, definition: ToolDefinition, handler: ToolHandler) -> None:
        """Register a tool definition and its implementation."""
        if definition.name in self._definitions:
            raise ValueError(f"Tool '{definition.name}' is already registered")

        self._definitions[definition.name] = definition
        self._handlers[definition.name] = handler

    def get_definition(self, tool_name: str) -> ToolDefinition:
        """Return a registered definition or raise for an unknown tool."""
        try:
            return self._definitions[tool_name]
        except KeyError as error:
            raise ToolExecutionError(f"Unknown tool: '{tool_name}'") from error

    def list_definitions(self) -> list[ToolDefinition]:
        """Return all registered tool definitions."""
        return list(self._definitions.values())

    def execute(self, call: ToolCall) -> ToolResult:
        """Run a registered handler and capture its result or failure."""
        try:
            self.get_definition(call.tool_name)
        except ToolExecutionError as error:
            return ToolResult(
                tool_name=call.tool_name,
                success=False,
                error=str(error),
            )

        handler = self._handlers[call.tool_name]
        try:
            data = handler(call.arguments)
        except Exception as error:
            return ToolResult(
                tool_name=call.tool_name,
                success=False,
                error=str(error),
            )

        return ToolResult(tool_name=call.tool_name, success=True, data=data)
