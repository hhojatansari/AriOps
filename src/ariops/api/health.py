"""Health check API route."""

from fastapi import APIRouter

from ariops.config import settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Return the service health status."""
    return {"status": "ok", "service": settings.app_name}
