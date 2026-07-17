"""Tests for bounded tool-result evidence collection."""

from ariops.application.evidence_collection import EvidenceCollectionService
from ariops.application.tools import ToolRegistry
from ariops.domain.incidents import EvidenceType, Incident, Severity
from ariops.domain.tools import ToolCall
from ariops.infrastructure.k8s.fake_tools import register_fake_kubernetes_tools


def make_incident() -> Incident:
    """Create an incident for evidence collection tests."""
    return Incident(
        title="API errors",
        source="monitoring",
        severity=Severity.CRITICAL,
    )


def make_service() -> EvidenceCollectionService:
    """Create a collection service backed by fake Kubernetes tools."""
    registry = ToolRegistry()
    register_fake_kubernetes_tools(registry)
    return EvidenceCollectionService(registry)


def test_successful_tool_result_creates_and_attaches_evidence() -> None:
    """Successful tool data is stored as incident evidence."""
    incident = make_incident()

    evidence = make_service().collect(
        incident,
        [ToolCall("k8s.get_pods", {"namespace": "payments"})],
    )

    assert len(evidence) == 1
    assert incident.evidence == evidence
    assert evidence[0].source == "k8s.get_pods"
    assert evidence[0].summary == "Collected data from k8s.get_pods"
    assert evidence[0].raw == {
        "pods": [{"name": "api-123", "namespace": "payments", "phase": "Running"}]
    }


def test_log_tool_maps_to_log_evidence() -> None:
    """Log tools produce log evidence."""
    evidence = make_service().collect(
        make_incident(),
        [
            ToolCall(
                "k8s.get_pod_logs",
                {"namespace": "payments", "pod_name": "api-123"},
            )
        ],
    )

    assert evidence[0].type is EvidenceType.LOG


def test_event_tool_maps_to_event_evidence() -> None:
    """Event tools produce event evidence."""
    evidence = make_service().collect(
        make_incident(),
        [ToolCall("k8s.get_events", {"namespace": "payments"})],
    )

    assert evidence[0].type is EvidenceType.EVENT


def test_deployment_tool_maps_to_deployment_state_evidence() -> None:
    """Deployment tools produce deployment-state evidence."""
    evidence = make_service().collect(
        make_incident(),
        [
            ToolCall(
                "k8s.get_deployment",
                {"namespace": "payments", "deployment_name": "api"},
            )
        ],
    )

    assert evidence[0].type is EvidenceType.DEPLOYMENT_STATE


def test_failed_tool_result_creates_manual_note_evidence() -> None:
    """Unknown tools are represented as manual-note failure evidence."""
    evidence = make_service().collect(
        make_incident(),
        [ToolCall("k8s.missing", {})],
    )

    assert evidence[0].type is EvidenceType.MANUAL_NOTE
    assert evidence[0].source == "k8s.missing"
    assert evidence[0].summary == "Tool execution failed: Unknown tool: 'k8s.missing'"
    assert evidence[0].raw == {"error": "Unknown tool: 'k8s.missing'"}


def test_collect_returns_all_created_evidence() -> None:
    """One evidence item is returned for each attempted tool call."""
    incident = make_incident()
    evidence = make_service().collect(
        incident,
        [
            ToolCall("k8s.get_pods", {"namespace": "payments"}),
            ToolCall("k8s.get_events", {"namespace": "payments"}),
            ToolCall("k8s.missing", {}),
        ],
    )

    assert len(evidence) == 3
    assert incident.evidence == evidence
