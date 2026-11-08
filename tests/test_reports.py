from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_daily_stats_returns_a_list():
    r = client.get("/stats/daily?days=7")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_failures_requires_an_endpoint():
    assert client.get("/failures").status_code == 422