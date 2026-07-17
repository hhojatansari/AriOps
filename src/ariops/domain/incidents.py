"""Framework-independent incident investigation models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class Severity(str, Enum):
    """Incident severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Lifecycle states for an incident investigation."""

    NEW = "new"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FAILED = "failed"


class EvidenceType(str, Enum):
    """Types of information collected during an investigation."""

    ALERT = "alert"
    LOG = "log"
    EVENT = "event"
    METRIC = "metric"
    RESOURCE_STATE = "resource_state"
    DEPLOYMENT_STATE = "deployment_state"
    TRACE = "trace"
    MANUAL_NOTE = "manual_note"


class RecommendationRisk(str, Enum):
    """Risk levels for recommended actions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Evidence:
    """A piece of information supporting an incident investigation."""

    type: EvidenceType
    source: str
    summary: str
    raw: dict[str, Any] | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class Finding:
    """An assessed conclusion drawn from incident evidence."""

    title: str
    description: str
    confidence: float
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Validate that confidence is a probability."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


@dataclass
class Recommendation:
    """A suggested response to an incident finding."""

    title: str
    description: str
    risk: RecommendationRisk
    action: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class Incident:
    """The aggregate root for an incident investigation."""

    title: str
    severity: Severity
    source: str
    namespace: str | None = None
    resource: str | None = None
    status: IncidentStatus = IncidentStatus.NEW
    evidence: list[Evidence] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def add_evidence(self, evidence: Evidence) -> None:
        """Attach evidence to this incident."""
        self.evidence.append(evidence)
        self._touch()

    def add_finding(self, finding: Finding) -> None:
        """Attach a finding to this incident."""
        self.findings.append(finding)
        self._touch()

    def add_recommendation(self, recommendation: Recommendation) -> None:
        """Attach a recommendation to this incident."""
        self.recommendations.append(recommendation)
        self._touch()

    def mark_investigating(self) -> None:
        """Mark the incident as under investigation."""
        self.status = IncidentStatus.INVESTIGATING
        self._touch()

    def mark_resolved(self) -> None:
        """Mark the incident as resolved."""
        self.status = IncidentStatus.RESOLVED
        self._touch()

    def mark_failed(self) -> None:
        """Mark the incident investigation as failed."""
        self.status = IncidentStatus.FAILED
        self._touch()

    def _touch(self) -> None:
        """Update the modification timestamp."""
        self.updated_at = utc_now()
