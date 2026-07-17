"""Definitions for the Kubernetes tools available to investigations."""

from ariops.domain.tools import ToolDefinition


def get_kubernetes_tool_definitions() -> list[ToolDefinition]:
    """Return the bounded set of Kubernetes investigation tool contracts."""
    return [
        ToolDefinition(
            name="k8s.get_pods",
            description="List pods in a namespace, optionally filtered by label selector.",
            input_schema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "label_selector": {"type": "string"},
                },
                "required": ["namespace"],
            },
            output_schema={
                "type": "object",
                "properties": {"pods": {"type": "array"}},
                "required": ["pods"],
            },
        ),
        ToolDefinition(
            name="k8s.get_pod",
            description="Retrieve the current state of a named pod.",
            input_schema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "pod_name": {"type": "string"},
                },
                "required": ["namespace", "pod_name"],
            },
            output_schema={
                "type": "object",
                "properties": {"pod": {"type": "object"}},
                "required": ["pod"],
            },
        ),
        ToolDefinition(
            name="k8s.get_pod_logs",
            description="Retrieve recent logs from a pod container.",
            input_schema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "pod_name": {"type": "string"},
                    "container": {"type": "string"},
                    "previous": {"type": "boolean", "default": False},
                    "tail_lines": {"type": "integer", "default": 200},
                },
                "required": ["namespace", "pod_name"],
            },
            output_schema={
                "type": "object",
                "properties": {"logs": {"type": "string"}},
                "required": ["logs"],
            },
        ),
        ToolDefinition(
            name="k8s.get_events",
            description="List Kubernetes events in a namespace, optionally for an object.",
            input_schema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "involved_object_name": {"type": "string"},
                    "involved_object_kind": {"type": "string"},
                },
                "required": ["namespace"],
            },
            output_schema={
                "type": "object",
                "properties": {"events": {"type": "array"}},
                "required": ["events"],
            },
        ),
        ToolDefinition(
            name="k8s.get_deployment",
            description="Retrieve the current state of a named deployment.",
            input_schema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "deployment_name": {"type": "string"},
                },
                "required": ["namespace", "deployment_name"],
            },
            output_schema={
                "type": "object",
                "properties": {"deployment": {"type": "object"}},
                "required": ["deployment"],
            },
        ),
    ]
