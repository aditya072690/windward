from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200


def test_meta():
    r = client.get("/api/v1/meta")
    assert r.status_code == 200
    data = r.json()
    assert "data_as_of" in data


def test_decision_forecast():
    r = client.get("/api/v1/decision-forecast?decision_date=2026-01-15&cutoff=09:00&view=decision")
    assert r.status_code == 200
    data = r.json()
    assert len(data["points"]) == 48
    assert "mae_mw" in data["summary"]


def test_decision_forecast_latest():
    r = client.get("/api/v1/decision-forecast?decision_date=2026-01-15&cutoff=09:00&view=latest")
    assert r.status_code == 200
    data = r.json()
    assert data["cutoff_utc"] is None


def test_ledger():
    r = client.get("/api/v1/accuracy/ledger?decision_date=2026-01-15")
    assert r.status_code == 200
    data = r.json()
    assert len(data["rows"]) == 8
