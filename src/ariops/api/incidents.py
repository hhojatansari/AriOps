"""Incident investigation API routes and schemas."""

from uuid import UUID

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ariops.application.investigations import InvestigationService
from ariops.domain.incidents import EvidenceType, Incident, IncidentStatus, Severity
from ariops.infrastructure.persistence.database import get_db_session
from ariops.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyIncidentRepository,
)

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


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


class EvidenceResponse(BaseModel):
    """Persisted evidence returned for an incident."""

    id: UUID
    type: EvidenceType
    source: str
    summary: str
    raw: dict[str, Any] | None
    created_at: datetime


class IncidentResponse(BaseModel):
    """A persisted incident and its accumulated evidence."""

    incident_id: UUID
    status: IncidentStatus
    title: str
    source: str
    severity: Severity
    namespace: str | None
    resource: str | None
    created_at: datetime
    updated_at: datetime
    evidence: list[EvidenceResponse]


def get_investigation_service(
    session: Session = Depends(get_db_session),
) -> InvestigationService:
    """Build an investigation service backed by the request database session."""
    return InvestigationService(SqlAlchemyIncidentRepository(session))


def to_incident_response(incident: Incident) -> IncidentResponse:
    """Map an incident aggregate to its API representation."""
    return IncidentResponse(
        incident_id=incident.id,
        status=incident.status,
        title=incident.title,
        source=incident.source,
        severity=incident.severity,
        namespace=incident.namespace,
        resource=incident.resource,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        evidence=[
            EvidenceResponse(
                id=item.id,
                type=item.type,
                source=item.source,
                summary=item.summary,
                raw=item.raw,
                created_at=item.created_at,
            )
            for item in incident.evidence
        ],
    )


@router.post("/investigate", response_model=InvestigateIncidentResponse)
def investigate_incident(
    request: InvestigateIncidentRequest,
    investigation_service: InvestigationService = Depends(get_investigation_service),
) -> InvestigateIncidentResponse:
    """Start and persist an incident investigation workflow."""
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


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: UUID,
    session: Session = Depends(get_db_session),
) -> IncidentResponse:
    """Return a persisted incident and the evidence collected so far."""
    incident = SqlAlchemyIncidentRepository(session).get(incident_id)
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found.",
        )
    return to_incident_response(incident)
