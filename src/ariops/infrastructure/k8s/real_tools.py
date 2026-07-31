"""Registration of real read-only Kubernetes investigation tools."""

from ariops.application.tools import ToolHandler, ToolRegistry
from ariops.config import Settings
from ariops.infrastructure.k8s.client import KubernetesToolClient
from ariops.infrastructure.k8s.tool_definitions import (
    get_kubernetes_tool_definitions,
)


def register_kubernetes_tools(registry: ToolRegistry, settings: Settings) -> None:
    """Register real read-only Kubernetes handlers for every tool contract."""
    tool_client = KubernetesToolClient(settings)
    handlers: dict[str, ToolHandler] = {
        "k8s.get_pods": tool_client.get_pods,
        "k8s.get_pod": tool_client.get_pod,
        "k8s.get_pod_logs": tool_client.get_pod_logs,
        "k8s.get_events": tool_client.get_events,
        "k8s.get_deployment": tool_client.get_deployment,
    }
    for definition in get_kubernetes_tool_definitions():
        registry.register(definition, handlers[definition.name])
