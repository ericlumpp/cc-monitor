from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
BASE = {
    "canvas_id": "t",
    "step_id": "s",
    "user_id": "u",
    "endpoint": "https://api.example.com/x",
}


def test_create_event():
    r = client.post("/events", json={**BASE, "payload": {"country": "US"}})
    assert r.status_code == 201
    assert "id" in r.json()


def test_oversized_payload_rejected():
    r = client.post("/events", json={**BASE, "payload": {"blob": "x" * 5000}})
    assert r.status_code == 413


def test_missing_endpoint_rejected():
    body = {k: v for k, v in BASE.items() if k != "endpoint"}
    assert client.post("/events", json=body).status_code == 422
