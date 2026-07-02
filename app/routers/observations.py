"""
Observation endpoints — add a vital sign, and query a patient's vitals with filters.

The query endpoint calls crud.query_observations(), which YOU implement.
Once you fill in that CRUD function, this endpoint works as-is.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.logging_config import log_event

router = APIRouter(prefix="/patients/{patient_id}/observations", tags=["observations"])
log = logging.getLogger("app.observations")


@router.post("", response_model=schemas.ObservationRead, status_code=status.HTTP_201_CREATED)
def add_observation(
    patient_id: str, data: schemas.ObservationCreate, db: Session = Depends(get_db)
):
    if crud.get_patient(db, patient_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "patient not found")
    obs = crud.add_observation(db, patient_id, data)
    log_event(log, "observation_added", patient_id=patient_id, code=obs.code, value=obs.value)
    return obs


@router.get("", response_model=list[schemas.ObservationRead])
def query_observations(
    patient_id: str,
    code: str | None = Query(default=None, description="LOINC code filter, e.g. 8867-4"),
    start: datetime | None = Query(default=None, description="ISO start of time window"),
    end: datetime | None = Query(default=None, description="ISO end of time window"),
    db: Session = Depends(get_db),
):
    if crud.get_patient(db, patient_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "patient not found")
    return crud.query_observations(db, patient_id, code=code, start=start, end=end)
