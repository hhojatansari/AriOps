"""Tests for the bounded tool registry contract."""

from typing import Any

import pytest

from ariops.application.tools import ToolRegistry
from ariops.domain.tools import (
    ToolCall,
    ToolDefinition,
    ToolExecutionError,
)


def make_definition() -> ToolDefinition:
    """Create a representative tool definition."""
    return ToolDefinition(
        name="echo",
        description="Returns its provided value.",
        input_schema={"type": "object"},
    )


def echo_handler(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return a value from the tool arguments."""
    return {"value": arguments["value"]}


def test_registering_and_listing_a_tool() -> None:
    """Registered definitions are available from the registry."""
    registry = ToolRegistry()
    definition = make_definition()

    registry.register(definition, echo_handler)

    assert registry.list_definitions() == [definition]


def test_duplicate_registration_raises_value_error() -> None:
    """Tool names must be unique."""
    registry = ToolRegistry()
    definition = make_definition()
    registry.register(definition, echo_handler)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(definition, echo_handler)


def test_get_definition_returns_registered_definition() -> None:
    """Definitions can be retrieved by name."""
    registry = ToolRegistry()
    definition = make_definition()
    registry.register(definition, echo_handler)

    assert registry.get_definition("echo") is definition


def test_get_definition_for_unknown_tool_raises_execution_error() -> None:
    """Unknown definitions raise the domain execution error."""
    with pytest.raises(ToolExecutionError, match="Unknown tool"):
        ToolRegistry().get_definition("missing")


def test_executing_a_registered_tool_returns_successful_result() -> None:
    """Registered handlers return their result data."""
    registry = ToolRegistry()
    registry.register(make_definition(), echo_handler)

    result = registry.execute(ToolCall(tool_name="echo", arguments={"value": "ok"}))

    assert result.success is True
    assert result.data == {"value": "ok"}
    assert result.error is None


def test_executing_an_unknown_tool_returns_failed_result() -> None:
    """Unknown tools produce a failed result rather than raising."""
    result = ToolRegistry().execute(ToolCall(tool_name="missing", arguments={}))

    assert result.success is False
    assert result.error == "Unknown tool: 'missing'"


def test_handler_exception_returns_failed_result() -> None:
    """Handler errors are captured in a failed result."""
    registry = ToolRegistry()

    def failing_handler(arguments: dict[str, Any]) -> dict[str, Any]:
        del arguments
        raise RuntimeError("tool failed")

    registry.register(make_definition(), failing_handler)

    result = registry.execute(ToolCall(tool_name="echo", arguments={}))

    assert result.success is False
    assert result.error == "tool failed"
