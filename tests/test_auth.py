def test_events_require_a_key(anon):
    assert anon.post("/events", json={}).status_code == 401


def test_wrong_key_is_rejected(anon):
    r = anon.get("/anomalies", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401


def test_health_stays_public(anon):
    assert anon.get("/health").status_code == 200


def test_valid_key_is_accepted(client):
    assert client.get("/anomalies").status_code == 200