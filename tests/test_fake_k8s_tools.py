"""Tests for local fake Kubernetes tool handlers."""

from ariops.application.tools import ToolRegistry
from ariops.domain.tools import ToolCall
from ariops.infrastructure.k8s.fake_tools import register_fake_kubernetes_tools


def make_registry() -> ToolRegistry:
    """Create a registry populated with fake Kubernetes tools."""
    registry = ToolRegistry()
    register_fake_kubernetes_tools(registry)
    return registry


def test_registering_fake_tools_registers_all_kubernetes_tools() -> None:
    """All Kubernetes tool definitions are available in the registry."""
    registry = make_registry()

    assert len(registry.list_definitions()) == 5


def test_fake_tools_execute_successfully() -> None:
    """Every fake Kubernetes tool returns a successful result."""
    registry = make_registry()
    calls = [
        ToolCall("k8s.get_pods", {"namespace": "payments"}),
        ToolCall("k8s.get_pod", {"namespace": "payments", "pod_name": "api-123"}),
        ToolCall(
            "k8s.get_pod_logs",
            {"namespace": "payments", "pod_name": "api-123"},
        ),
        ToolCall("k8s.get_events", {"namespace": "payments"}),
        ToolCall(
            "k8s.get_deployment",
            {"namespace": "payments", "deployment_name": "api"},
        ),
    ]

    results = [registry.execute(call) for call in calls]

    assert all(result.success for result in results)


def test_fake_tools_echo_relevant_resource_arguments() -> None:
    """Fake resource responses preserve their requested identifiers."""
    registry = make_registry()

    pods = registry.execute(ToolCall("k8s.get_pods", {"namespace": "payments"}))
    pod = registry.execute(
        ToolCall(
            "k8s.get_pod",
            {"namespace": "payments", "pod_name": "api-123"},
        )
    )
    deployment = registry.execute(
        ToolCall(
            "k8s.get_deployment",
            {"namespace": "payments", "deployment_name": "api"},
        )
    )

    assert pods.data == {
        "pods": [{"name": "api-123", "namespace": "payments", "phase": "Running"}]
    }
    assert pod.data == {
        "pod": {
            "name": "api-123",
            "namespace": "payments",
            "phase": "Running",
            "restart_count": 0,
        }
    }
    assert deployment.data == {
        "deployment": {
            "name": "api",
            "namespace": "payments",
            "ready_replicas": 1,
            "replicas": 1,
        }
    }
