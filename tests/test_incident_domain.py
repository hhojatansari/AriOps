"""Tests for incident domain models."""

import pytest

from ariops.domain.incidents import (
    Evidence,
    EvidenceType,
    Finding,
    Incident,
    IncidentStatus,
    Severity,
)


def make_incident() -> Incident:
    """Create an incident suitable for domain tests."""
    return Incident(
        title="Checkout errors",
        severity=Severity.CRITICAL,
        source="monitoring",
    )


def test_incident_defaults_to_new() -> None:
    """New incidents begin in the new status."""
    incident = make_incident()

    assert incident.status is IncidentStatus.NEW


def test_adding_evidence_updates_evidence_list() -> None:
    """Evidence can be attached to an incident."""
    incident = make_incident()
    evidence = Evidence(
        type=EvidenceType.ALERT,
        source="prometheus",
        summary="Error rate exceeded threshold.",
    )

    incident.add_evidence(evidence)

    assert incident.evidence == [evidence]


def test_invalid_finding_confidence_raises_value_error() -> None:
    """Finding confidence must be a probability."""
    with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
        Finding(
            title="Probable deployment regression",
            description="Errors started after the latest deployment.",
            confidence=1.1,
        )


def test_status_transition_methods_update_status() -> None:
    """Incident lifecycle helpers set their corresponding statuses."""
    incident = make_incident()

    incident.mark_investigating()
    assert incident.status is IncidentStatus.INVESTIGATING

    incident.mark_resolved()
    assert incident.status is IncidentStatus.RESOLVED

    incident.mark_failed()
    assert incident.status is IncidentStatus.FAILED
