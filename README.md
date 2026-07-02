# Patient Vitals API

A production-ready **FastAPI + SQLAlchemy 2.0** service for managing **FHIR-style healthcare data**, including patient demographics and clinical vital signs. The application supports **PostgreSQL** for production deployments and **SQLite** for zero-setup local development, with **Alembic** migrations, **pytest** testing, and structured JSON logging.

The project demonstrates modern backend engineering practices commonly used in healthcare technology platforms.

## Features

- FastAPI REST API
- SQLAlchemy 2.0 ORM
- PostgreSQL and SQLite support
- Alembic database migrations
- FHIR-style Patient and Observation resources
- Dynamic filtering and querying of observations
- Structured JSON logging
- Automated test suite with pytest
- FHIR Bundle ingestion script

## FHIR Resources Modeled

### Patient

Stores patient demographic and identity information.

### Observation

Stores clinical measurements such as:

- Heart Rate
- Body Temperature
- Blood Pressure
- Other vital-sign observations

Each observation is associated with a patient and timestamped for historical tracking.

---

## Architecture

```mermaid
graph TD
    Client[Client / FHIR Bundle Script]
    Client --> FastAPI[FastAPI Routers]

    FastAPI --> Schemas[Pydantic Schemas]
    Schemas --> CRUD[CRUD Layer]

    CRUD --> ORM[SQLAlchemy 2.0 ORM]
    ORM --> DB[(SQLite / PostgreSQL)]

    DB --> CRUD
```

---

## Quick Start

### Create Virtual Environment

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

to access the interactive Swagger UI.

---

## Run Tests

```bash
pytest -q
```

All tests should pass successfully.

---

## Project Structure

```text
app/
├── config.py
├── database.py
├── logging_config.py
├── models.py
├── schemas.py
├── crud.py
└── routers/
    ├── patients.py
    └── observations.py

alembic/
├── versions/
└── env.py

scripts/
└── ingest_fhir.py

sample_data/
└── fhir_bundle.json

tests/
```

### Key Components

| File              | Purpose                                    |
| ----------------- | ------------------------------------------ |
| config.py         | Application configuration                  |
| database.py       | Engine, Session, and dependency management |
| models.py         | SQLAlchemy ORM models                      |
| schemas.py        | Pydantic validation schemas                |
| crud.py           | Database access layer                      |
| routers/          | API endpoints                              |
| logging_config.py | Structured JSON logging                    |
| alembic/          | Database migrations                        |
| tests/            | Automated test suite                       |

---

## FHIR Bundle Ingestion

A sample FHIR R4 bundle is included for testing ingestion workflows.

Start the API:

```bash
uvicorn app.main:app --reload
```

In another terminal:

```bash
python scripts/ingest_fhir.py sample_data/fhir_bundle.json
```

The ingestion script converts FHIR resources into API requests and stores them in the database.

---

## Production Setup (PostgreSQL)

Start PostgreSQL:

```bash
docker compose up -d
```

Configure the database:

```bash
export DATABASE_URL=postgresql+psycopg://vitals:vitals@localhost:5432/vitals
```

Create and apply migrations:

```bash
alembic revision --autogenerate -m "create patients and observations"
alembic upgrade head
```

Run the application:

```bash
uvicorn app.main:app --reload
```

---

## Technical Skills Demonstrated

| Skill Area              | Implementation                           |
| ----------------------- | ---------------------------------------- |
| Backend Development     | FastAPI                                  |
| API Design              | RESTful endpoints                        |
| Data Modeling           | SQLAlchemy ORM                           |
| Database Management     | PostgreSQL, SQLite                       |
| Migrations              | Alembic                                  |
| Testing                 | pytest                                   |
| Logging & Observability | Structured JSON logging                  |
| Healthcare Standards    | FHIR Patient and Observation resources   |
| Query Optimization      | Dynamic SQLAlchemy filtering and sorting |

---

## What I Learned

This project provided hands-on experience with:

- Designing REST APIs using FastAPI
- Modeling healthcare data using FHIR-inspired resources
- Building dynamic database queries with SQLAlchemy 2.0
- Managing schema evolution with Alembic
- Writing automated tests using pytest
- Implementing structured application logging
- Working with both SQLite and PostgreSQL environments

The completed observation query implementation demonstrates conditional query construction, filtering, sorting, and efficient ORM-based database interaction patterns commonly used in production healthcare applications.
