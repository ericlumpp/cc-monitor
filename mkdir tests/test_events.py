from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
BASE = {"canvas_id": "t", "step_id": "s", "user_id": "u"}


def test_create_event():
    r = client.post("/events", json={**BASE, "status": "success"})
    assert r.status_code == 201
    assert "id" in r.json()


def test_error_requires_cause():
    r = client.post("/events", json={**BASE, "status": "error"})
    assert r.status_code == 422