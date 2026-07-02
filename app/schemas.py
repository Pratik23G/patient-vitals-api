"""
Pydantic v2 schemas = the shape of data crossing the API boundary.

Split into `Create` (what the client sends) and `Read` (what we return, including
server-generated fields like id/created_at). `from_attributes=True` lets a schema
be built directly from an ORM object.
"""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- Observation ----------
class ObservationCreate(BaseModel):
    code: str = Field(examples=["8867-4"])
    display: str = Field(examples=["Heart rate"])
    value: float = Field(examples=[72.0])
    unit: str = Field(examples=["beats/minute"])
    effective_time: datetime


class ObservationRead(ObservationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    patient_id: str
    created_at: datetime


# ---------- Patient ----------
class PatientCreate(BaseModel):
    identifier: str = Field(examples=["MRN-001"])
    family_name: str = Field(examples=["Doe"])
    given_name: str = Field(examples=["Jane"])
    birth_date: date | None = None
    gender: str | None = Field(default=None, examples=["female"])


class PatientRead(PatientCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
