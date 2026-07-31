"""Service catalog API routes."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ariops.domain.services import KubernetesDeployment, Service
from ariops.infrastructure.persistence.database import get_db_session
from ariops.infrastructure.persistence.sqlalchemy_repositories import SqlAlchemyServiceCatalogRepository

router = APIRouter(prefix="/api/v1/services", tags=["services"])


class KubernetesDeploymentRequest(BaseModel):
    cluster_name: str
    namespace: str
    deployment_name: str


class CreateServiceRequest(BaseModel):
    name: str
    description: str | None = None
    owner: str | None = None
    kubernetes_deployments: list[KubernetesDeploymentRequest]


class ServiceResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    owner: str | None
    enabled: bool
    created_at: datetime


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(request: CreateServiceRequest, session: Session = Depends(get_db_session)) -> ServiceResponse:
    service = Service(name=request.name, description=request.description, owner=request.owner)
    deployments = [KubernetesDeployment(service_id=service.id, **item.model_dump()) for item in request.kubernetes_deployments]
    SqlAlchemyServiceCatalogRepository(session).create(service, deployments)
    return ServiceResponse(id=service.id, name=service.name, description=service.description,
                           owner=service.owner, enabled=service.enabled, created_at=service.created_at)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: UUID, session: Session = Depends(get_db_session)) -> ServiceResponse:
    service = SqlAlchemyServiceCatalogRepository(session).get(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found.")
    return ServiceResponse(id=service.id, name=service.name, description=service.description,
                           owner=service.owner, enabled=service.enabled, created_at=service.created_at)
