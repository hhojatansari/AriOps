"""Application configuration."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    app_name: str = "ariops"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://ariops:ariops@localhost:5432/ariops"
    kubernetes_tool_adapter: Literal["real", "fake"] = "real"
    kubernetes_connection_mode: Literal["kubeconfig", "in_cluster"] = "kubeconfig"
    kubernetes_cluster_name: str = "default"
    kubernetes_kubeconfig_path: str | None = None
    kubernetes_allowed_namespaces: str = ""
    kubernetes_request_timeout_seconds: int = 10
    kubernetes_max_log_tail_lines: int = 200

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ARIOPS_")

    @property
    def allowed_kubernetes_namespaces(self) -> frozenset[str]:
        """Return the configured namespace allowlist; ``*`` permits all."""
        return frozenset(
            namespace.strip()
            for namespace in self.kubernetes_allowed_namespaces.split(",")
            if namespace.strip()
        )


settings = Settings()
