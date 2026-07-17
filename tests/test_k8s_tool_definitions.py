"""Tests for Kubernetes tool contracts."""

from ariops.infrastructure.k8s.tool_definitions import (
    get_kubernetes_tool_definitions,
)


def test_kubernetes_tool_definitions_have_expected_contracts() -> None:
    """The registry-ready Kubernetes tool set is complete and distinct."""
    definitions = get_kubernetes_tool_definitions()
    names = {definition.name for definition in definitions}

    assert len(definitions) == 5
    assert names == {
        "k8s.get_pods",
        "k8s.get_pod",
        "k8s.get_pod_logs",
        "k8s.get_events",
        "k8s.get_deployment",
    }
    assert len(names) == len(definitions)
    assert all(definition.description for definition in definitions)
    assert all(definition.input_schema["type"] == "object" for definition in definitions)
    assert all(definition.output_schema is not None for definition in definitions)
