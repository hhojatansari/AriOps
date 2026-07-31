"""Application service for starting incident investigations."""

from ariops.domain.incidents import Incident, Severity
from ariops.domain.repositories import IncidentRepository


class InvestigationService:
    """Start the lifecycle of an incident investigation."""

    def __init__(self, incident_repository: IncidentRepository) -> None:
        self._incident_repository = incident_repository

    def start_investigation(
        self,
        *,
        title: str,
        source: str,
        severity: Severity,
        namespace: str | None = None,
        resource: str | None = None,
        symptom: str | None = None,
    ) -> Incident:
        """Create an incident and mark it as under investigation.

        The symptom is accepted as part of the initial contract and will be
        used by a future investigation workflow.
        """
        del symptom

        incident = Incident(
            title=title,
            source=source,
            severity=severity,
            namespace=namespace,
            resource=resource,
        )
        incident.mark_investigating()
        return self._incident_repository.save(incident)
