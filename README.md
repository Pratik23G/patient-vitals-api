# Patient Vitals API

A small **FastAPI + SQLAlchemy 2.0** service over **FHIR-style** patient and vital-sign
data, backed by **Postgres** (SQLite for zero-setup local dev), with **Alembic**
migrations, **pytest** tests, and structured JSON logging.

Two core [FHIR](https://www.hl7.org/fhir/) resources are modeled as tables:
`Patient` and `Observation` (vital signs — heart rate, temperature, etc.). You can
create patients, record vitals, query a patient's vitals with code/time filters, and
ingest a real FHIR `Bundle`.

> Built to learn the Clinical Ink backend stack the honest way: build it, understand
> it, *then* put it on the résumé. See "What's left for you" before you claim it.

---

## Quick start (60 seconds, no database to install)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/docs  (interactive Swagger UI)
```

Run the tests:

```bash
pytest -q
```

You'll see **7 pass, 4 fail** — that's expected. The 4 failures are the feature you
implement (below).

---

## What's left for you (this is the point)

Open `app/crud.py` and implement `query_observations()`. It's marked `TODO(pratik)`
with step-by-step hints. The 4 failing tests in `tests/test_observations.py` are the
exact spec — run `pytest tests/test_observations.py -v` and make them green.

That one function is where you actually learn SQLAlchemy's query API (conditional
`.where()` chaining, `.order_by()`, executing and scalar-mapping results). Don't skip
it — being able to explain that code cold is what makes this project defensible in an
interview. The reference solution is at the very bottom of this file; try it yourself
first.

Stretch goals (each teaches something real):
- Add pagination (`limit` / `offset`) to the query endpoint + a test.
- Add an `average` endpoint (mean value for a code over a window) using `func.avg`.
- Validate that `value` is non-negative with a Pydantic field validator + a test.

---

## Project layout

```
app/
  config.py          settings (DATABASE_URL, log level)
  database.py        engine, Session, Base, get_db dependency   <- read first
  models.py          Patient & Observation ORM models           <- the FHIR mapping
  schemas.py         Pydantic request/response shapes
  crud.py            all DB access (Patient done; Observation query = your TODO)
  logging_config.py  structured JSON logging
  routers/           patients.py, observations.py (HTTP layer)
alembic/             migrations (env.py wired to app settings)
scripts/ingest_fhir.py   parse a FHIR Bundle -> API calls
sample_data/fhir_bundle.json   a real FHIR R4 Bundle to ingest
tests/               pytest suite (SQLite in-memory, no Postgres needed)
```

## Ingest the FHIR bundle

```bash
uvicorn app.main:app --reload        # in one terminal
python scripts/ingest_fhir.py sample_data/fhir_bundle.json   # in another
```

This maps FHIR `Patient` / `Observation` resources (nested `identifier`, `name`,
`code.coding`, `valueQuantity`, `effectiveDateTime`) into your tables — so "worked with
FHIR data" is literally true.

## Using real Postgres + Alembic (the production path)

```bash
docker compose up -d
export DATABASE_URL=postgresql+psycopg://vitals:vitals@localhost:5432/vitals
alembic revision --autogenerate -m "create patients and observations"
alembic upgrade head
uvicorn app.main:app --reload
```

## How it maps to the job description

| Clinical Ink asks for            | Where it is here                                   |
|----------------------------------|----------------------------------------------------|
| Python backend, API endpoints    | `app/routers/*`, FastAPI                            |
| Data models & migrations         | `app/models.py`, `alembic/`                         |
| SQLAlchemy / Postgres            | `database.py`, `models.py`, `crud.py`               |
| Meaningful tests (correctness)   | `tests/` — behavior asserted, not hoped             |
| Observability / instrument       | `logging_config.py` structured events               |
| Healthcare data (FHIR/wearables) | FHIR bundle ingest; Observation = wearable vitals   |
| Verify-it mindset                | you make the red tests green before claiming it     |

---

<details>
<summary>Reference solution for query_observations (try it yourself first!)</summary>

```python
def query_observations(db, patient_id, code=None, start=None, end=None):
    stmt = select(models.Observation).where(models.Observation.patient_id == patient_id)
    if code is not None:
        stmt = stmt.where(models.Observation.code == code)
    if start is not None:
        stmt = stmt.where(models.Observation.effective_time >= start)
    if end is not None:
        stmt = stmt.where(models.Observation.effective_time <= end)
    stmt = stmt.order_by(models.Observation.effective_time.desc())
    return list(db.execute(stmt).scalars())
```

Each conditional `.where()` returns a new statement; they AND together. That's the
whole pattern.
</details>
