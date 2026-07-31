"""Domain contracts for incident persistence."""

from typing import Protocol
from uuid import UUID

from ariops.domain.incidents import Incident


class IncidentRepository(Protocol):
    """Persist and retrieve complete incident aggregates."""

    def save(self, incident: Incident) -> Incident:
        """Create or update an incident aggregate."""

    def get(self, incident_id: UUID) -> Incident | None:
        """Return an incident aggregate when it exists."""
