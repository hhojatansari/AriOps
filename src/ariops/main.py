"""FastAPI application entrypoint."""

from fastapi import FastAPI

from ariops.api.health import router as health_router
from ariops.api.incidents import router as incidents_router
from ariops.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(incidents_router)
