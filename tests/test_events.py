import uuid

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
    r = client.post("/events", json={**BASE, "user_id": str(uuid.uuid4()), "payload": {"country": "US"}})
    assert r.status_code == 201
    assert "id" in r.json()


def test_duplicate_post_is_ignored():
    body = {**BASE, "user_id": str(uuid.uuid4()), "payload": {"country": "US"}}
    first = client.post("/events", json=body)
    second = client.post("/events", json=body)
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json() == {"id": first.json()["id"], "duplicate": True}


def test_oversized_payload_rejected():
    r = client.post("/events", json={**BASE, "payload": {"blob": "x" * 5000}})
    assert r.status_code == 413


def test_missing_endpoint_rejected():
    body = {k: v for k, v in BASE.items() if k != "endpoint"}
    assert client.post("/events", json=body).status_code == 422