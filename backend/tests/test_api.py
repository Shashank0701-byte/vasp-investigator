import hashlib
import json

from fastapi.testclient import TestClient

from app.main import app
from app.providers import DEMO_TARGET, address
from app.storage import CaseStore


def test_full_case_lifecycle(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path}/test.db"
    monkeypatch.setenv("DATABASE_URL", url)
    with TestClient(app) as client:
        assert client.get("/api/health").json()["live_ingestion"] is False
        response = client.post("/api/cases", json={"target": DEMO_TARGET})
        assert response.status_code == 201
        case = response.json()
        assert client.get("/api/cases").json()[0]["id"] == case["id"]
        assert client.get("/api/cases/" + case["id"]).json() == case
        report = client.get("/api/cases/" + case["id"] + "/report")
        assert report.status_code == 200
        assert "synthetic evidence" in report.text
        assert "not ownership probabilities" in report.text
        evidence = client.get("/api/cases/" + case["id"] + "/evidence").json()
        digest = hashlib.sha256(
            json.dumps(
                evidence["evidence"], sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        assert digest == case["evidence_digest"]
        store = CaseStore(url)
        assert store.get(case["id"])["id"] == case["id"]
        store.engine.dispose()
        assert client.get("/api/cases/not-found").status_code == 404
        assert client.post("/api/cases", json={"target": "bad"}).status_code == 422
        assert (
            client.post("/api/cases", json={"target": address(123)}).status_code == 422
        )
        imported = client.post(
            "/api/cases",
            json={
                "target": address(0),
                "mode": "import",
                "transactions": [],
                "labels": [],
            },
        )
        assert imported.status_code == 201
        assert imported.json()["analysis"]["candidates"] == []
