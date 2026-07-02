"""
Patient endpoint tests — these all pass out of the box. Read them to see the pattern:
arrange (create data) -> act (call endpoint) -> assert (prove the exact outcome).
"""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_patient(client):
    resp = client.post("/patients", json={
        "identifier": "MRN-001", "family_name": "Doe", "given_name": "Jane",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["identifier"] == "MRN-001"
    assert body["id"]          # server generated a UUID
    assert body["created_at"]  # server set the timestamp


def test_duplicate_identifier_is_rejected(client):
    payload = {"identifier": "MRN-DUP", "family_name": "A", "given_name": "B"}
    assert client.post("/patients", json=payload).status_code == 201
    # Second create with same identifier must 409, not 500.
    assert client.post("/patients", json=payload).status_code == 409


def test_get_patient_404(client):
    assert client.get("/patients/does-not-exist").status_code == 404


def test_get_and_list_patient(client, sample_patient):
    pid = sample_patient["id"]
    assert client.get(f"/patients/{pid}").json()["id"] == pid
    listed = client.get("/patients").json()
    assert any(p["id"] == pid for p in listed)
