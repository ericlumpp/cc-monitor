from app.anomaly import common_values


def test_common_values_finds_only_the_dominant_pair():
    payloads = [
        {"country": "DE", "plan": "free" if i % 2 else "pro"} for i in range(10)
    ] + [{"country": "US", "plan": "pro"}]
    result = common_values(payloads)
    assert [(k, v) for k, v, _ in result] == [("country", "DE")]