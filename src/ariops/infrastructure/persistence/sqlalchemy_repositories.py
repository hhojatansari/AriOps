"""SQLAlchemy implementations of domain repository contracts."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ariops.domain.incidents import (
    Evidence,
    EvidenceType,
    Finding,
    Incident,
    IncidentStatus,
    Recommendation,
    RecommendationRisk,
    Severity,
)
from ariops.infrastructure.persistence.models import (
    EvidenceModel,
    FindingModel,
    IncidentModel,
    RecommendationModel,
)


class SqlAlchemyIncidentRepository:
    """Persist complete incident aggregates through SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, incident: Incident) -> Incident:
        """Store an incident and all currently attached investigation data."""
        self._session.merge(self._to_model(incident))
        self._session.commit()
        return incident

    def get(self, incident_id: UUID) -> Incident | None:
        """Load an incident with all evidence, findings, and recommendations."""
        statement = (
            select(IncidentModel)
            .where(IncidentModel.id == incident_id)
            .options(
                selectinload(IncidentModel.evidence),
                selectinload(IncidentModel.findings),
                selectinload(IncidentModel.recommendations),
            )
        )
        model = self._session.scalar(statement)
        return self._to_domain(model) if model is not None else None

    @staticmethod
    def _to_model(incident: Incident) -> IncidentModel:
        model = IncidentModel(
            id=incident.id,
            title=incident.title,
            severity=incident.severity.value,
            source=incident.source,
            namespace=incident.namespace,
            resource=incident.resource,
            status=incident.status.value,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
        )
        model.evidence = [
            EvidenceModel(
                id=item.id,
                type=item.type.value,
                source=item.source,
                summary=item.summary,
                raw=item.raw,
                created_at=item.created_at,
            )
            for item in incident.evidence
        ]
        model.findings = [
            FindingModel(
                id=item.id,
                title=item.title,
                description=item.description,
                confidence=item.confidence,
                created_at=item.created_at,
            )
            for item in incident.findings
        ]
        model.recommendations = [
            RecommendationModel(
                id=item.id,
                title=item.title,
                description=item.description,
                risk=item.risk.value,
                action=item.action,
                created_at=item.created_at,
            )
            for item in incident.recommendations
        ]
        return model

    @staticmethod
    def _to_domain(model: IncidentModel) -> Incident:
        return Incident(
            id=model.id,
            title=model.title,
            severity=Severity(model.severity),
            source=model.source,
            namespace=model.namespace,
            resource=model.resource,
            status=IncidentStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            evidence=[
                Evidence(
                    id=item.id,
                    type=EvidenceType(item.type),
                    source=item.source,
                    summary=item.summary,
                    raw=item.raw,
                    created_at=item.created_at,
                )
                for item in model.evidence
            ],
            findings=[
                Finding(
                    id=item.id,
                    title=item.title,
                    description=item.description,
                    confidence=item.confidence,
                    created_at=item.created_at,
                )
                for item in model.findings
            ],
            recommendations=[
                Recommendation(
                    id=item.id,
                    title=item.title,
                    description=item.description,
                    risk=RecommendationRisk(item.risk),
                    action=item.action,
                    created_at=item.created_at,
                )
                for item in model.recommendations
            ],
        )
