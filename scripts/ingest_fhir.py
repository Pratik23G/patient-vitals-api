"""
Ingest a FHIR R4 Bundle into the running API.

This is what makes "FHIR" honest on your resume: you parse actual FHIR resources
(Patient, Observation) and map their nested fields into your own data model.

Usage (start the API first, then):
    python scripts/ingest_fhir.py sample_data/fhir_bundle.json

It maps:
    FHIR Patient.identifier[0].value      -> patient.identifier
    FHIR Patient.name[0].family/given     -> family_name / given_name
    FHIR Observation.code.coding[0]       -> code / display
    FHIR Observation.valueQuantity        -> value / unit
    FHIR Observation.effectiveDateTime    -> effective_time
    FHIR Observation.subject.reference    -> which patient it belongs to
"""
import sys
from pathlib import Path

import httpx

API = "http://127.0.0.1:8000"


def _first(lst, default=None):
    return lst[0] if lst else default


def ingest(bundle_path: str) -> None:
    bundle = __import__("json").loads(Path(bundle_path).read_text())
    resources = [e["resource"] for e in bundle.get("entry", [])]

    # Map FHIR Patient.id -> our created patient id, so observations can be linked.
    fhir_id_to_our_id: dict[str, str] = {}

    with httpx.Client(base_url=API, timeout=10) as client:
        # Patients first.
        for r in [x for x in resources if x["resourceType"] == "Patient"]:
            name = _first(r.get("name", []), {})
            payload = {
                "identifier": _first(r.get("identifier", []), {}).get("value", r["id"]),
                "family_name": name.get("family", "Unknown"),
                "given_name": _first(name.get("given", []), "Unknown"),
                "gender": r.get("gender"),
                "birth_date": r.get("birthDate"),
            }
            resp = client.post("/patients", json=payload)
            if resp.status_code == 409:
                # Already ingested — look it up so we can still link observations.
                existing = client.get("/patients").json()
                match = next(p for p in existing if p["identifier"] == payload["identifier"])
                fhir_id_to_our_id[r["id"]] = match["id"]
            else:
                resp.raise_for_status()
                fhir_id_to_our_id[r["id"]] = resp.json()["id"]
            print(f"patient  {r['id']} -> {fhir_id_to_our_id[r['id']]}")

        # Then observations.
        for r in [x for x in resources if x["resourceType"] == "Observation"]:
            ref = r["subject"]["reference"].split("/")[-1]  # "Patient/pat-fhir-1" -> "pat-fhir-1"
            our_pid = fhir_id_to_our_id.get(ref)
            if our_pid is None:
                print(f"  ! skipping observation {r['id']}: patient {ref} not found")
                continue
            coding = _first(r["code"]["coding"], {})
            qty = r.get("valueQuantity", {})
            payload = {
                "code": coding.get("code", "unknown"),
                "display": coding.get("display", "unknown"),
                "value": qty.get("value", 0.0),
                "unit": qty.get("unit", ""),
                "effective_time": r["effectiveDateTime"],
            }
            resp = client.post(f"/patients/{our_pid}/observations", json=payload)
            resp.raise_for_status()
            print(f"obs      {r['id']} -> {resp.json()['id']}  ({payload['display']} {payload['value']}{payload['unit']})")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_data/fhir_bundle.json"
    ingest(path)
    print("done.")
