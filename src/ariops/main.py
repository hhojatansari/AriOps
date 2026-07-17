"""FastAPI application entrypoint."""

from fastapi import FastAPI

from ariops.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health() -> dict[str, str]:
    """Return the service health status."""
    return {"status": "ok", "service": settings.app_name}
