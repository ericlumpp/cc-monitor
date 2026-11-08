import os
import random
import sys
from datetime import datetime, timedelta, timezone

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
KEY = os.environ["CC_MONITOR_API_KEY"]
HEADERS = {"Authorization": f"Bearer {KEY}"}
ENDPOINTS = [
    "https://api.example.com/recs",
    "https://api.example.com/profile",
    "https://api.example.com/offers",
]
COUNTRIES = ["US", "CA", "GB", "DE", "FR"]
now = datetime.now(timezone.utc)


def send(endpoint, country, when):
    body = {
        "canvas_id": "demo-canvas",
        "step_id": f"step_{random.randint(1, 3)}",
        "user_id": f"user_{random.randint(1, 500)}",
        "endpoint": endpoint,
        "payload": {"country": country, "plan": random.choice(["free", "pro"])},
        "occurred_at": when.isoformat(),
    }
    for _ in range(2):  # Braze sends every failure twice
        httpx.post(f"{BASE}/events", json=body, headers=HEADERS).raise_for_status()


# Background noise: 100 scattered failures over the previous ~23 hours.
for _ in range(100):
    when = now - timedelta(minutes=random.randint(60, 1440))
    send(random.choice(ENDPOINTS), random.choice(COUNTRIES), when)

# The incident: 40 failures in the last 30 minutes, all on /offers, ~90% from DE.
for _ in range(40):
    country = "DE" if random.random() < 0.9 else random.choice(COUNTRIES)
    send(ENDPOINTS[2], country, now - timedelta(minutes=random.randint(0, 30)))

print("done")