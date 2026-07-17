# AriOps

Minimal FastAPI service scaffold for AriOps.

## Local development

Requires Python 3.12.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn ariops.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

Run tests with:

```bash
pytest
```
