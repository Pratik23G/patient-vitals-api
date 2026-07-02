"""
Observation tests.

The `add_observation` tests pass now. The `query_*` tests are RED until you implement
crud.query_observations() (see the TODO there). They are the spec — make them green.

Run just these while you work:  pytest tests/test_observations.py -v
"""
import pytest


def _add(client, pid, code, display, value, unit, when):
    return client.post(f"/patients/{pid}/observations", json={
        "code": code, "display": display, "value": value, "unit": unit,
        "effective_time": when,
    })


def test_add_observation(client, sample_patient):
    pid = sample_patient["id"]
    resp = _add(client, pid, "8867-4", "Heart rate", 72.0, "beats/minute",
                "2026-01-01T08:00:00Z")
    assert resp.status_code == 201
    assert resp.json()["value"] == 72.0
    assert resp.json()["patient_id"] == pid


def test_add_observation_unknown_patient_404(client):
    resp = _add(client, "nope", "8867-4", "Heart rate", 72.0, "beats/minute",
                "2026-01-01T08:00:00Z")
    assert resp.status_code == 404


# ---- The following require crud.query_observations() to be implemented ----

def test_query_returns_all_for_patient(client, sample_patient):
    pid = sample_patient["id"]
    _add(client, pid, "8867-4", "Heart rate", 72.0, "beats/minute", "2026-01-01T08:00:00Z")
    _add(client, pid, "8310-5", "Body temperature", 37.0, "Cel", "2026-01-01T09:00:00Z")
    resp = client.get(f"/patients/{pid}/observations")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_query_filters_by_code(client, sample_patient):
    pid = sample_patient["id"]
    _add(client, pid, "8867-4", "Heart rate", 72.0, "beats/minute", "2026-01-01T08:00:00Z")
    _add(client, pid, "8310-5", "Body temperature", 37.0, "Cel", "2026-01-01T09:00:00Z")
    resp = client.get(f"/patients/{pid}/observations", params={"code": "8867-4"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["code"] == "8867-4"


def test_query_filters_by_time_window(client, sample_patient):
    pid = sample_patient["id"]
    _add(client, pid, "8867-4", "Heart rate", 70.0, "beats/minute", "2026-01-01T08:00:00Z")
    _add(client, pid, "8867-4", "Heart rate", 75.0, "beats/minute", "2026-01-02T08:00:00Z")
    _add(client, pid, "8867-4", "Heart rate", 80.0, "beats/minute", "2026-01-03T08:00:00Z")
    resp = client.get(f"/patients/{pid}/observations", params={
        "start": "2026-01-02T00:00:00Z", "end": "2026-01-02T23:59:59Z",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["value"] == 75.0


def test_query_orders_newest_first(client, sample_patient):
    pid = sample_patient["id"]
    _add(client, pid, "8867-4", "Heart rate", 70.0, "beats/minute", "2026-01-01T08:00:00Z")
    _add(client, pid, "8867-4", "Heart rate", 80.0, "beats/minute", "2026-01-03T08:00:00Z")
    body = client.get(f"/patients/{pid}/observations").json()
    # newest (Jan 3) should come first
    assert body[0]["value"] == 80.0
    assert body[1]["value"] == 70.0
