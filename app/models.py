"""
ORM models — the heart of the SQLAlchemy learning.

These two tables mirror two core FHIR resources:
  - Patient      -> https://www.hl7.org/fhir/patient.html
  - Observation  -> https://www.hl7.org/fhir/observation.html  (we model vital signs)

SQLAlchemy 2.0 style uses typed `Mapped[...]` annotations + `mapped_column(...)`.
The relationship() call is what lets you write `patient.observations` in Python and
have SQLAlchemy issue the right JOIN/second query for you.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    # A medical record number / FHIR identifier. Unique so we never double-ingest a patient.
    identifier: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    family_name: Mapped[str] = mapped_column(String(128))
    given_name: Mapped[str] = mapped_column(String(128))
    birth_date: Mapped[date | None] = mapped_column(default=None)
    gender: Mapped[str | None] = mapped_column(String(16), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # One patient has many observations. cascade means deleting a patient deletes their vitals.
    observations: Mapped[list[Observation]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
    )


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), index=True)

    # FHIR Observation.code — we store a LOINC-style code + human label.
    code: Mapped[str] = mapped_column(String(32), index=True)        # e.g. "8867-4"
    display: Mapped[str] = mapped_column(String(128))                # e.g. "Heart rate"
    value: Mapped[float] = mapped_column()                           # e.g. 72.0
    unit: Mapped[str] = mapped_column(String(32))                    # e.g. "beats/minute"
    effective_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    patient: Mapped[Patient] = relationship(back_populates="observations")
