"""Health endpoint tests."""

from fastapi.testclient import TestClient

from ariops.main import app


def test_health() -> None:
    """The health endpoint reports the service as available."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ariops"}
