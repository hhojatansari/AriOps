"""Collect investigation evidence through bounded tool calls."""

from ariops.application.tools import ToolRegistry
from ariops.domain.incidents import Evidence, EvidenceType, Incident
from ariops.domain.tools import ToolCall, ToolResult


class EvidenceCollectionService:
    """Execute tool calls and attach their results to an incident."""

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry

    def collect(self, incident: Incident, tool_calls: list[ToolCall]) -> list[Evidence]:
        """Collect evidence from each tool call and attach it to an incident."""
        evidence_items: list[Evidence] = []

        for call in tool_calls:
            result = self._tool_registry.execute(call)
            evidence = self._to_evidence(result)
            incident.add_evidence(evidence)
            evidence_items.append(evidence)

        return evidence_items

    def _to_evidence(self, result: ToolResult) -> Evidence:
        """Map a tool result into the corresponding incident evidence."""
        if result.success:
            return Evidence(
                type=self._evidence_type_for_tool(result.tool_name),
                source=result.tool_name,
                summary=f"Collected data from {result.tool_name}",
                raw=result.data,
            )

        error = result.error or "Unknown tool execution error"
        return Evidence(
            type=EvidenceType.MANUAL_NOTE,
            source=result.tool_name,
            summary=f"Tool execution failed: {error}",
            raw={"error": error},
        )

    @staticmethod
    def _evidence_type_for_tool(tool_name: str) -> EvidenceType:
        """Infer the evidence type represented by a Kubernetes tool name."""
        if "logs" in tool_name:
            return EvidenceType.LOG
        if "events" in tool_name:
            return EvidenceType.EVENT
        if "deployment" in tool_name:
            return EvidenceType.DEPLOYMENT_STATE
        return EvidenceType.RESOURCE_STATE
