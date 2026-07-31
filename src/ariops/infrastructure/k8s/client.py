"""Read-only Kubernetes API adapter for investigation tools."""

from datetime import datetime
from typing import Any

from kubernetes import client, config

from ariops.config import Settings


class KubernetesAccessError(ValueError):
    """Raised when a requested Kubernetes read is outside the configured scope."""


class KubernetesToolClient:
    """Execute bounded, read-only Kubernetes investigation queries."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        configuration = client.Configuration()
        if settings.kubernetes_connection_mode == "in_cluster":
            config.load_incluster_config(client_configuration=configuration)
        else:
            config.load_kube_config(
                config_file=settings.kubernetes_kubeconfig_path,
                client_configuration=configuration,
            )

        api_client = client.ApiClient(configuration=configuration)
        self._core_api = client.CoreV1Api(api_client=api_client)
        self._apps_api = client.AppsV1Api(api_client=api_client)

    def get_pods(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """List pod summaries in an allowed namespace."""
        namespace = self._allowed_namespace(arguments)
        response = self._core_api.list_namespaced_pod(
            namespace=namespace,
            label_selector=arguments.get("label_selector"),
            _request_timeout=self._settings.kubernetes_request_timeout_seconds,
        )
        return {"pods": [self._pod_summary(pod) for pod in response.items]}

    def get_pod(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Read the current state of one pod in an allowed namespace."""
        namespace = self._allowed_namespace(arguments)
        pod = self._core_api.read_namespaced_pod(
            name=self._required_argument(arguments, "pod_name"),
            namespace=namespace,
            _request_timeout=self._settings.kubernetes_request_timeout_seconds,
        )
        return {"pod": self._pod_summary(pod)}

    def get_pod_logs(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Read a bounded number of log lines from one pod."""
        namespace = self._allowed_namespace(arguments)
        requested_tail_lines = int(
            arguments.get("tail_lines", self._settings.kubernetes_max_log_tail_lines)
        )
        tail_lines = max(
            1,
            min(requested_tail_lines, self._settings.kubernetes_max_log_tail_lines),
        )
        logs = self._core_api.read_namespaced_pod_log(
            name=self._required_argument(arguments, "pod_name"),
            namespace=namespace,
            container=arguments.get("container"),
            previous=bool(arguments.get("previous", False)),
            tail_lines=tail_lines,
            _request_timeout=self._settings.kubernetes_request_timeout_seconds,
        )
        return {"logs": logs}

    def get_events(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """List event summaries in an allowed namespace."""
        namespace = self._allowed_namespace(arguments)
        response = self._core_api.list_namespaced_event(
            namespace=namespace,
            _request_timeout=self._settings.kubernetes_request_timeout_seconds,
        )
        expected_name = arguments.get("involved_object_name")
        expected_kind = arguments.get("involved_object_kind")
        events = [
            self._event_summary(event)
            for event in response.items
            if self._matches_involved_object(event, expected_name, expected_kind)
        ]
        return {"events": events}

    def get_deployment(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Read the current state of one deployment in an allowed namespace."""
        namespace = self._allowed_namespace(arguments)
        deployment = self._apps_api.read_namespaced_deployment(
            name=self._required_argument(arguments, "deployment_name"),
            namespace=namespace,
            _request_timeout=self._settings.kubernetes_request_timeout_seconds,
        )
        deployment_status = deployment.status
        return {
            "deployment": {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "ready_replicas": deployment_status.ready_replicas or 0,
                "replicas": deployment_status.replicas or 0,
                "available_replicas": deployment_status.available_replicas or 0,
                "updated_replicas": deployment_status.updated_replicas or 0,
            }
        }

    def _allowed_namespace(self, arguments: dict[str, Any]) -> str:
        namespace = self._required_argument(arguments, "namespace")
        allowed_namespaces = self._settings.allowed_kubernetes_namespaces
        if "*" not in allowed_namespaces and namespace not in allowed_namespaces:
            raise KubernetesAccessError(
                f"Namespace '{namespace}' is not in the Kubernetes allowlist"
            )
        return namespace

    @staticmethod
    def _required_argument(arguments: dict[str, Any], name: str) -> str:
        value = arguments.get(name)
        if not isinstance(value, str) or not value:
            raise KubernetesAccessError(f"Tool argument '{name}' is required")
        return value

    @staticmethod
    def _pod_summary(pod: Any) -> dict[str, Any]:
        container_statuses = pod.status.container_statuses or []
        return {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "phase": pod.status.phase,
            "restart_count": sum(status.restart_count for status in container_statuses),
            "node_name": pod.spec.node_name,
        }

    @staticmethod
    def _event_summary(event: Any) -> dict[str, Any]:
        involved_object = event.involved_object
        return {
            "reason": event.reason,
            "message": event.message,
            "type": event.type,
            "involved_object_name": involved_object.name if involved_object else None,
            "involved_object_kind": involved_object.kind if involved_object else None,
            "last_timestamp": KubernetesToolClient._timestamp(event.last_timestamp),
        }

    @staticmethod
    def _matches_involved_object(
        event: Any, expected_name: Any, expected_kind: Any
    ) -> bool:
        involved_object = event.involved_object
        if expected_name and (not involved_object or involved_object.name != expected_name):
            return False
        return not expected_kind or (
            involved_object is not None and involved_object.kind == expected_kind
        )

    @staticmethod
    def _timestamp(value: datetime | None) -> str | None:
        return value.isoformat() if value is not None else None
