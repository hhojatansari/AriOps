# AriOps

Minimal FastAPI service scaffold for AriOps.

## Local development

Requires Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --index-url https://pypi.efrda.ir -e ".[dev]"
uvicorn ariops.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

Run tests with:

```bash
pytest
```

## Docker

Build and run the service using the configured private Python registry:

```bash
docker build -t ariops .
docker run --rm -p 8000:8000 ariops
```
