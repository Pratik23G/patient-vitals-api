"""
FastAPI application entrypoint.

Run locally:  uvicorn app.main:app --reload
Then open:    http://127.0.0.1:8000/docs   (interactive Swagger UI, free with FastAPI)
"""
import logging

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.logging_config import configure_logging, log_event
from app.routers import observations, patients

configure_logging(settings.log_level)
log = logging.getLogger("app")

# For local/dev convenience we create tables on startup. In production you'd rely on
# Alembic migrations instead (see alembic/ and the README) and NOT call create_all.
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(patients.router)
app.include_router(observations.router)


@app.get("/health", tags=["meta"])
def health():
    log_event(log, "health_check")
    return {"status": "ok", "service": settings.app_name}
