"""Local fake implementations of Kubernetes investigation tools."""

from typing import Any

from ariops.application.tools import ToolHandler, ToolRegistry
from ariops.infrastructure.k8s.tool_definitions import (
    get_kubernetes_tool_definitions,
)


def register_fake_kubernetes_tools(registry: ToolRegistry) -> None:
    """Register deterministic local handlers for all Kubernetes tools."""
    handlers: dict[str, ToolHandler] = {
        "k8s.get_pods": _get_pods,
        "k8s.get_pod": _get_pod,
        "k8s.get_pod_logs": _get_pod_logs,
        "k8s.get_events": _get_events,
        "k8s.get_deployment": _get_deployment,
    }

    for definition in get_kubernetes_tool_definitions():
        registry.register(definition, handlers[definition.name])


def _get_pods(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return a representative running pod."""
    return {
        "pods": [
            {
                "name": "api-123",
                "namespace": arguments["namespace"],
                "phase": "Running",
            }
        ]
    }


def _get_pod(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return a representative pod state."""
    return {
        "pod": {
            "name": arguments["pod_name"],
            "namespace": arguments["namespace"],
            "phase": "Running",
            "restart_count": 0,
        }
    }


def _get_pod_logs(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic placeholder pod logs."""
    del arguments
    return {"logs": "fake log line 1\nfake log line 2"}


def _get_events(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return a representative Kubernetes event."""
    del arguments
    return {"events": [{"reason": "Started", "message": "Started container api"}]}


def _get_deployment(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return a representative deployment state."""
    return {
        "deployment": {
            "name": arguments["deployment_name"],
            "namespace": arguments["namespace"],
            "ready_replicas": 1,
            "replicas": 1,
        }
    }
