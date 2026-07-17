"""Tests for the incident investigation endpoint."""

from uuid import UUID

from fastapi.testclient import TestClient

from ariops.main import app

client = TestClient(app)


def test_investigate_incident_starts_placeholder_workflow() -> None:
    """Starting an investigation returns its initial domain state."""
    response = client.post(
        "/api/v1/incidents/investigate",
        json={
            "title": "Checkout errors",
            "source": "monitoring",
            "severity": "critical",
            "namespace": "payments",
            "resource": "deployment/checkout",
            "symptom": "HTTP 500 error rate increased",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "investigating"
    assert UUID(payload["incident_id"])
    assert payload["title"] == "Checkout errors"
    assert payload["severity"] == "critical"
    assert payload["message"] == "Investigation workflow is not implemented yet."
