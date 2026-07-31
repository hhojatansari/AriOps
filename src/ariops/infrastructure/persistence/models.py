"""SQLAlchemy models for AriOps persistence."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    """Base class for database models."""


class ServiceModel(Base):
    __tablename__ = "services"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    kubernetes_deployments: Mapped[list["ServiceKubernetesDeploymentModel"]] = relationship(back_populates="service")


class ServiceKubernetesDeploymentModel(Base):
    __tablename__ = "service_kubernetes_deployments"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    service_id: Mapped[UUID] = mapped_column(ForeignKey("services.id"), index=True)
    cluster_name: Mapped[str] = mapped_column(String(255))
    namespace: Mapped[str] = mapped_column(String(255))
    deployment_name: Mapped[str] = mapped_column(String(255))
    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    service: Mapped[ServiceModel] = relationship(back_populates="kubernetes_deployments")


class IncidentModel(Base):
    """Stored incident aggregate root."""

    __tablename__ = "incidents"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(32))
    source: Mapped[str] = mapped_column(String(255))
    namespace: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource: Mapped[str | None] = mapped_column(String(512), nullable=True)
    service_id: Mapped[UUID | None] = mapped_column(ForeignKey("services.id"), nullable=True, index=True)
    service_kubernetes_deployment_id: Mapped[UUID | None] = mapped_column(ForeignKey("service_kubernetes_deployments.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    evidence: Mapped[list["EvidenceModel"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )
    findings: Mapped[list["FindingModel"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["RecommendationModel"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )


class EvidenceModel(Base):
    """Stored evidence collected during an investigation."""

    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"), index=True)
    type: Mapped[str] = mapped_column(String(32))
    source: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    raw: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    incident: Mapped[IncidentModel] = relationship(back_populates="evidence")


class FindingModel(Base):
    """Stored root-cause finding."""

    __tablename__ = "findings"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    incident: Mapped[IncidentModel] = relationship(back_populates="findings")


class RecommendationModel(Base):
    """Stored remediation recommendation."""

    __tablename__ = "recommendations"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    risk: Mapped[str] = mapped_column(String(32))
    action: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    incident: Mapped[IncidentModel] = relationship(back_populates="recommendations")
