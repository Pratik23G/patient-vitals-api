"""Patient endpoints — full CRUD, your worked example for the API layer."""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.logging_config import log_event

router = APIRouter(prefix="/patients", tags=["patients"])
log = logging.getLogger("app.patients")


@router.post("", response_model=schemas.PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(data: schemas.PatientCreate, db: Session = Depends(get_db)):
    if crud.get_patient_by_identifier(db, data.identifier):
        # Enforce the unique-identifier rule with a clean 409 instead of a DB crash.
        raise HTTPException(status.HTTP_409_CONFLICT, f"identifier {data.identifier} already exists")
    patient = crud.create_patient(db, data)
    log_event(log, "patient_created", patient_id=patient.id, identifier=patient.identifier)
    return patient


@router.get("", response_model=list[schemas.PatientRead])
def list_patients(limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_patients(db, limit=limit)


@router.get("/{patient_id}", response_model=schemas.PatientRead)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "patient not found")
    return patient
