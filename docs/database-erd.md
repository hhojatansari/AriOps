# AriOps Database ERD

The initial PostgreSQL schema persists investigation records. An incident is the
aggregate root; it can have many evidence items, findings, and recommendations.

```mermaid
erDiagram
    SERVICES ||--o{ SERVICE_KUBERNETES_DEPLOYMENTS : has
    SERVICES ||--o{ INCIDENTS : investigated_by
    SERVICE_KUBERNETES_DEPLOYMENTS ||--o{ INCIDENTS : targets
    INCIDENTS ||--o{ EVIDENCE : contains
    INCIDENTS ||--o{ FINDINGS : produces
    INCIDENTS ||--o{ RECOMMENDATIONS : includes

    SERVICES {
        uuid id PK
        varchar name
        text description
        varchar owner
        boolean enabled
    }

    SERVICE_KUBERNETES_DEPLOYMENTS {
        uuid id PK
        uuid service_id FK
        varchar cluster_name
        varchar namespace
        varchar deployment_name
        boolean enabled
    }

    INCIDENTS {
        uuid id PK
        varchar title
        varchar severity
        varchar source
        varchar namespace
        varchar resource
        uuid service_id FK
        uuid service_kubernetes_deployment_id FK
        varchar status
        timestamptz created_at
        timestamptz updated_at
    }

    EVIDENCE {
        uuid id PK
        uuid incident_id FK
        varchar type
        varchar source
        text summary
        json raw
        timestamptz created_at
    }

    FINDINGS {
        uuid id PK
        uuid incident_id FK
        varchar title
        text description
        float confidence
        timestamptz created_at
    }

    RECOMMENDATIONS {
        uuid id PK
        uuid incident_id FK
        varchar title
        text description
        varchar risk
        text action
        timestamptz created_at
    }
```

`incident_id` is a foreign key to `incidents.id` in each child table. The
database also contains Alembic's internal `alembic_version` table, which tracks
applied schema migrations and is not part of the application data model.
