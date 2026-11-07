from app.anomaly import common_values


def test_only_unusually_common_values_are_reported():
    # In the spike: every failure is DE, and 60% are "free".
    spike = [{"country": "DE", "plan": "free" if i < 6 else "pro"} for i in range(10)]
    # Normally: DE is rare (10%), but "free" is already 50%.
    baseline = [
        {"country": "DE" if i < 2 else "US", "plan": "free" if i < 10 else "pro"}
        for i in range(20)
    ]
    result = common_values(spike, baseline)
    assert [(k, v) for k, v, *_ in result] == [("country", "DE")]