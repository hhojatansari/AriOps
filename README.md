# AriOps

AriOps is an open-source AI-powered root cause analysis platform for Kubernetes and cloud infrastructure.

It investigates operational incidents by collecting evidence from infrastructure and observability systems, analyzing possible causes, and generating root cause findings with confidence and remediation recommendations.

The project follows a modular architecture that separates deterministic platform workflows from agent reasoning.

> AriOps is currently under active development.

## Documentation

* [Architecture](docs/architecture.md)
* [Investigation Flow](docs/investigation-flow.md)
* [Database ERD](docs/database-erd.md)

## Local Development

Requires Python 3.12.

The service requires PostgreSQL. Set `ARIOPS_DATABASE_URL` to a PostgreSQL
connection URL before starting it. The default local URL is:

```text
postgresql+psycopg://ariops:ariops@localhost:5432/ariops
```

```bash
python -m venv .venv
source .venv/bin/activate
pip install --index-url https://pypi.efrda.ir -e ".[dev]"
alembic upgrade head
uvicorn ariops.main:app --reload
```

The health endpoint is available at:

```text
http://127.0.0.1:8000/health
```

Start a deterministic Kubernetes investigation with:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/incidents/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Checkout errors",
    "source": "monitoring",
    "severity": "critical",
    "namespace": "payments",
    "resource": "deployment/checkout",
    "symptom": "HTTP 500 error rate increased"
  }'
```

The current workflow stores the alert context and collects a fixed initial set
of Kubernetes evidence through local fake tool adapters. A later step will
replace them with real Kubernetes integrations and agent-directed tool choice.

Run tests with:

```bash
pytest
```

## Docker

For a local PostgreSQL database and API service, use Docker Compose:

```bash
docker compose up --build
```

Compose runs the database migration before starting the API.
