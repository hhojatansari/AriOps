"""FastAPI application entrypoint."""

from fastapi import FastAPI

from ariops.api.health import router as health_router
from ariops.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
