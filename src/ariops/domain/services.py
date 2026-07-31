"""Framework-independent service catalog models."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from ariops.domain.incidents import utc_now


@dataclass
class Service:
    name: str
    description: str | None = None
    owner: str | None = None
    enabled: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class KubernetesDeployment:
    service_id: UUID
    cluster_name: str
    namespace: str
    deployment_name: str
    enabled: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
