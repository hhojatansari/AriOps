# AriOps

AriOps is an open-source AI-powered root cause analysis platform for Kubernetes and cloud infrastructure.

It investigates operational incidents by collecting evidence from infrastructure and observability systems, analyzing possible causes, and generating root cause findings with confidence and remediation recommendations.

The project follows a modular architecture that separates deterministic platform workflows from agent reasoning.

> AriOps is currently under active development.

## Documentation

* [Architecture](docs/architecture.md)
* [Investigation Flow](docs/investigation-flow.md)

## Local Development

Requires Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --index-url https://pypi.efrda.ir -e ".[dev]"
uvicorn ariops.main:app --reload
```

The health endpoint is available at:

```text
http://127.0.0.1:8000/health
```

Run tests with:

```bash
pytest
```

## Docker

```bash
docker build -t ariops .
docker run --rm -p 8000:8000 ariops
```
