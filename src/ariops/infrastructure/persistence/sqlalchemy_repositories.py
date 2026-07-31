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
from ariops.domain.services import KubernetesDeployment, Service
from ariops.infrastructure.persistence.models import (
    EvidenceModel,
    FindingModel,
    IncidentModel,
    RecommendationModel,
    ServiceKubernetesDeploymentModel,
    ServiceModel,
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
            service_id=incident.service_id,
            service_kubernetes_deployment_id=incident.service_kubernetes_deployment_id,
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
            service_id=model.service_id,
            service_kubernetes_deployment_id=model.service_kubernetes_deployment_id,
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


class SqlAlchemyServiceCatalogRepository:
    """SQLAlchemy service catalog adapter."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, service: Service, deployments: list[KubernetesDeployment]) -> Service:
        model = ServiceModel(
            id=service.id, name=service.name, description=service.description,
            owner=service.owner, enabled=service.enabled, created_at=service.created_at,
            updated_at=service.updated_at,
        )
        model.kubernetes_deployments = [
            ServiceKubernetesDeploymentModel(
                id=item.id, service_id=service.id, cluster_name=item.cluster_name,
                namespace=item.namespace, deployment_name=item.deployment_name,
                enabled=item.enabled, created_at=item.created_at, updated_at=item.updated_at,
            ) for item in deployments
        ]
        self._session.add(model)
        self._session.commit()
        return service

    def get(self, service_id: UUID) -> Service | None:
        model = self._session.get(ServiceModel, service_id)
        return self._to_service(model) if model else None

    def get_kubernetes_deployment(
        self, service_id: UUID, deployment_id: UUID | None = None
    ) -> KubernetesDeployment | None:
        statement = select(ServiceKubernetesDeploymentModel).where(
            ServiceKubernetesDeploymentModel.service_id == service_id,
            ServiceKubernetesDeploymentModel.enabled.is_(True),
        )
        if deployment_id:
            statement = statement.where(ServiceKubernetesDeploymentModel.id == deployment_id)
        models = list(self._session.scalars(statement))
        if len(models) != 1:
            return None
        return self._to_deployment(models[0])

    @staticmethod
    def _to_service(model: ServiceModel) -> Service:
        return Service(id=model.id, name=model.name, description=model.description,
                       owner=model.owner, enabled=model.enabled, created_at=model.created_at,
                       updated_at=model.updated_at)

    @staticmethod
    def _to_deployment(model: ServiceKubernetesDeploymentModel) -> KubernetesDeployment:
        return KubernetesDeployment(id=model.id, service_id=model.service_id,
            cluster_name=model.cluster_name, namespace=model.namespace,
            deployment_name=model.deployment_name, enabled=model.enabled,
            created_at=model.created_at, updated_at=model.updated_at)
