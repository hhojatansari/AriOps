"""Incident investigation API routes and schemas."""

from datetime import datetime
from functools import lru_cache
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ariops.application.evidence_collection import EvidenceCollectionService
from ariops.application.investigations import InvestigationService
from ariops.application.tools import ToolRegistry
from ariops.config import settings
from ariops.domain.incidents import EvidenceType, Incident, IncidentStatus, Severity
from ariops.infrastructure.persistence.database import get_db_session
from ariops.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyIncidentRepository,
    SqlAlchemyServiceCatalogRepository,
)
from ariops.infrastructure.k8s.fake_tools import register_fake_kubernetes_tools
from ariops.infrastructure.k8s.real_tools import register_kubernetes_tools

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


class InvestigateIncidentRequest(BaseModel):
    """Input required to begin an incident investigation."""

    title: str
    source: str
    severity: Severity
    namespace: str | None = None
    resource: str | None = None
    symptom: str | None = None
    service_id: UUID | None = None
    service_kubernetes_deployment_id: UUID | None = None


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
    service_id: UUID | None
    service_kubernetes_deployment_id: UUID | None
    created_at: datetime
    updated_at: datetime
    evidence: list[EvidenceResponse]


@lru_cache
def get_investigation_tool_registry() -> ToolRegistry:
    """Build the configured Kubernetes tool registry."""
    registry = ToolRegistry()
    if settings.kubernetes_tool_adapter == "fake":
        register_fake_kubernetes_tools(registry)
    else:
        register_kubernetes_tools(registry, settings)
    return registry


def get_investigation_service(
    session: Session = Depends(get_db_session),
) -> InvestigationService:
    """Build a request-scoped investigation workflow service."""
    registry = get_investigation_tool_registry()
    return InvestigationService(
        SqlAlchemyIncidentRepository(session),
        EvidenceCollectionService(registry),
        SqlAlchemyServiceCatalogRepository(session),
        settings.kubernetes_cluster_name,
    )


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
        service_id=incident.service_id,
        service_kubernetes_deployment_id=incident.service_kubernetes_deployment_id,
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


@router.post("/investigate", response_model=IncidentResponse)
def investigate_incident(
    request: InvestigateIncidentRequest,
    investigation_service: InvestigationService = Depends(get_investigation_service),
) -> IncidentResponse:
    """Run the initial deterministic investigation workflow and persist it."""
    try:
        incident = investigation_service.start_investigation(
            title=request.title, source=request.source, severity=request.severity,
            namespace=request.namespace, resource=request.resource, symptom=request.symptom,
            service_id=request.service_id,
            service_kubernetes_deployment_id=request.service_kubernetes_deployment_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error

    return to_incident_response(incident)


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
