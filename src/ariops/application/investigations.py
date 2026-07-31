"""Application service for deterministic incident investigations."""

from ariops.application.evidence_collection import EvidenceCollectionService
from ariops.domain.incidents import Evidence, EvidenceType, Incident, Severity
from ariops.domain.repositories import IncidentRepository
from ariops.domain.tools import ToolCall


class InvestigationService:
    """Run the bounded first stage of an incident investigation."""

    def __init__(
        self,
        incident_repository: IncidentRepository,
        evidence_collection_service: EvidenceCollectionService,
    ) -> None:
        self._incident_repository = incident_repository
        self._evidence_collection_service = evidence_collection_service

    def start_investigation(
        self,
        *,
        title: str,
        source: str,
        severity: Severity,
        namespace: str | None = None,
        resource: str | None = None,
        symptom: str | None = None,
    ) -> Incident:
        """Create, collect deterministic evidence for, and persist an incident."""

        incident = Incident(
            title=title,
            source=source,
            severity=severity,
            namespace=namespace,
            resource=resource,
        )
        incident.mark_investigating()

        if symptom:
            incident.add_evidence(
                Evidence(
                    type=EvidenceType.ALERT,
                    source=source,
                    summary=symptom,
                    raw={"symptom": symptom},
                )
            )

        self._evidence_collection_service.collect(
            incident,
            self._initial_tool_calls(namespace=namespace, resource=resource),
        )
        return self._incident_repository.save(incident)

    @staticmethod
    def _initial_tool_calls(
        *, namespace: str | None, resource: str | None
    ) -> list[ToolCall]:
        """Choose the fixed initial Kubernetes evidence set for an incident."""
        if namespace is None:
            return []

        tool_calls = [
            ToolCall("k8s.get_pods", {"namespace": namespace}),
            ToolCall("k8s.get_events", {"namespace": namespace}),
        ]
        resource_kind, separator, resource_name = (resource or "").partition("/")
        if not separator or not resource_name:
            return tool_calls

        if resource_kind == "pod":
            pod_arguments = {"namespace": namespace, "pod_name": resource_name}
            tool_calls.extend(
                [
                    ToolCall("k8s.get_pod", pod_arguments),
                    ToolCall("k8s.get_pod_logs", pod_arguments),
                ]
            )
        elif resource_kind == "deployment":
            tool_calls.append(
                ToolCall(
                    "k8s.get_deployment",
                    {"namespace": namespace, "deployment_name": resource_name},
                )
            )
        return tool_calls
