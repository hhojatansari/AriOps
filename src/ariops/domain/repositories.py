"""Domain contracts for incident persistence."""

from typing import Protocol
from uuid import UUID

from ariops.domain.incidents import Incident
from ariops.domain.services import KubernetesDeployment, Service


class IncidentRepository(Protocol):
    """Persist and retrieve complete incident aggregates."""

    def save(self, incident: Incident) -> Incident:
        """Create or update an incident aggregate."""

    def get(self, incident_id: UUID) -> Incident | None:
        """Return an incident aggregate when it exists."""


class ServiceCatalogRepository(Protocol):
    """Persist and resolve registered services and Kubernetes deployments."""

    def create(self, service: Service, deployments: list[KubernetesDeployment]) -> Service:
        """Create a service and its Kubernetes deployment targets."""

    def get(self, service_id: UUID) -> Service | None:
        """Return a registered service."""

    def get_kubernetes_deployment(
        self, service_id: UUID, deployment_id: UUID | None = None
    ) -> KubernetesDeployment | None:
        """Resolve the single enabled Kubernetes deployment for a service."""
