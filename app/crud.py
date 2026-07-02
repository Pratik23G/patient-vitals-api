"""
Data-access layer. Every DB read/write lives here so endpoints stay thin.

Patient operations are FULLY implemented as your worked example.
The Observation *query* function is left for you to write — that's the one that
actually teaches you SQLAlchemy filtering. See TODO(pratik) below.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas


# ---------- Patients (worked example — study this) ----------
def create_patient(db: Session, data: schemas.PatientCreate) -> models.Patient:
    patient = models.Patient(**data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)  # reloads server-set fields (id, created_at) from the DB
    return patient


def get_patient(db: Session, patient_id: str) -> models.Patient | None:
    # SQLAlchemy 2.0 style: build a select(), execute, take scalar (the ORM object).
    return db.execute(
        select(models.Patient).where(models.Patient.id == patient_id)
    ).scalar_one_or_none()


def get_patient_by_identifier(db: Session, identifier: str) -> models.Patient | None:
    return db.execute(
        select(models.Patient).where(models.Patient.identifier == identifier)
    ).scalar_one_or_none()


def list_patients(db: Session, limit: int = 100) -> list[models.Patient]:
    return list(db.execute(select(models.Patient).limit(limit)).scalars())


# ---------- Observations ----------
def add_observation(
    db: Session, patient_id: str, data: schemas.ObservationCreate
) -> models.Observation:
    obs = models.Observation(patient_id=patient_id, **data.model_dump())
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs


def query_observations(
    db: Session,
    patient_id: str,
    code: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[models.Observation]:
    """
    Return a patient's observations, optionally filtered by LOINC `code` and/or an
    [start, end] time window, newest first.

    TODO(pratik): implement this. This is THE function that teaches you SQLAlchemy
    querying, so write it yourself. Steps:
      1. Start:  stmt = select(models.Observation).where(
                     models.Observation.patient_id == patient_id)
      2. If `code` is given, chain another .where(models.Observation.code == code)
      3. If `start` is given, .where(models.Observation.effective_time >= start)
      4. If `end` is given,   .where(models.Observation.effective_time <= end)
      5. Order newest first:  .order_by(models.Observation.effective_time.desc())
      6. Execute + return a list:  return list(db.execute(stmt).scalars())

    Note: you can reassign `stmt = stmt.where(...)` conditionally — each .where()
    returns a NEW select, they AND together. That pattern is the whole lesson.

    The tests in tests/test_observations.py already assert the exact behavior above,
    so run `pytest` as you go and make them green.
    """
    stmt = select(models.Observation).where(models.Observation.patient_id == patient_id)

    if code:
        stmt = stmt.where(models.Observation.code == code)

    if start:
        stmt = stmt.where(models.Observation.effective_time >= start)

    if end:
        stmt = stmt.where(models.Observation.effective_time <= end)
   
    stmt = stmt.order_by(models.Observation.effective_time.desc())

    return list(db.execute(stmt).scalars())
