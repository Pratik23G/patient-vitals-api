"""
Application settings.

DATABASE_URL controls which database SQLAlchemy talks to.
  - Local quick start (no setup):  sqlite:///./vitals.db
  - Production-like (Postgres):     postgresql+psycopg://user:pass@localhost:5432/vitals

The tests override this entirely with an in-memory SQLite DB (see tests/conftest.py),
so you never need Postgres running just to run the test suite.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Default to a local SQLite file so `uvicorn app.main:app` works with zero setup.
    database_url: str = "sqlite:///./vitals.db"
    log_level: str = "INFO"
    app_name: str = "Patient Vitals API"


settings = Settings()
