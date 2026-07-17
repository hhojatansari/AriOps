"""Incident investigation API routes and schemas."""

from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from ariops.application.investigations import InvestigationService
from ariops.domain.incidents import IncidentStatus, Severity

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])
investigation_service = InvestigationService()


class InvestigateIncidentRequest(BaseModel):
    """Input required to begin an incident investigation."""

    title: str
    source: str
    severity: Severity
    namespace: str | None = None
    resource: str | None = None
    symptom: str | None = None


class InvestigateIncidentResponse(BaseModel):
    """Initial state returned when an investigation is started."""

    incident_id: UUID
    status: IncidentStatus
    title: str
    severity: Severity
    message: str


@router.post("/investigate", response_model=InvestigateIncidentResponse)
def investigate_incident(
    request: InvestigateIncidentRequest,
) -> InvestigateIncidentResponse:
    """Start an incident investigation workflow placeholder."""
    incident = investigation_service.start_investigation(
        title=request.title,
        source=request.source,
        severity=request.severity,
        namespace=request.namespace,
        resource=request.resource,
        symptom=request.symptom,
    )

    return InvestigateIncidentResponse(
        incident_id=incident.id,
        status=incident.status,
        title=incident.title,
        severity=incident.severity,
        message="Investigation workflow is not implemented yet.",
    )
