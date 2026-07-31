"""Add service catalog and incident target links."""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "20260731_02"
down_revision: str | None = "20260731_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table("services", sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text()), sa.Column("owner", sa.String(255)),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("service_kubernetes_deployments", sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("service_id", sa.Uuid(), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("cluster_name", sa.String(255), nullable=False), sa.Column("namespace", sa.String(255), nullable=False),
        sa.Column("deployment_name", sa.String(255), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_service_kubernetes_deployments_service_id", "service_kubernetes_deployments", ["service_id"])
    op.add_column("incidents", sa.Column("service_id", sa.Uuid(), nullable=True))
    op.add_column("incidents", sa.Column("service_kubernetes_deployment_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_incidents_service", "incidents", "services", ["service_id"], ["id"])
    op.create_foreign_key("fk_incidents_service_kubernetes_deployment", "incidents", "service_kubernetes_deployments", ["service_kubernetes_deployment_id"], ["id"])
    op.create_index("ix_incidents_service_id", "incidents", ["service_id"])
    op.create_index("ix_incidents_service_kubernetes_deployment_id", "incidents", ["service_kubernetes_deployment_id"])


def downgrade() -> None:
    op.drop_index("ix_incidents_service_kubernetes_deployment_id", table_name="incidents")
    op.drop_index("ix_incidents_service_id", table_name="incidents")
    op.drop_constraint("fk_incidents_service_kubernetes_deployment", "incidents", type_="foreignkey")
    op.drop_constraint("fk_incidents_service", "incidents", type_="foreignkey")
    op.drop_column("incidents", "service_kubernetes_deployment_id")
    op.drop_column("incidents", "service_id")
    op.drop_index("ix_service_kubernetes_deployments_service_id", table_name="service_kubernetes_deployments")
    op.drop_table("service_kubernetes_deployments")
    op.drop_table("services")
