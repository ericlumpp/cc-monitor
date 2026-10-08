import random
import sys

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
CAUSES = ["timeout", "http_500", "invalid_json"]
STEPS = ["step_1", "step_2", "step_3"]

for _ in range(200):
    step = random.choice(STEPS)
    failed = random.random() < (0.25 if step == "step_2" else 0.03)
    httpx.post(f"{BASE}/events", json={
        "canvas_id": "demo-canvas",
        "step_id": step,
        "user_id": f"user_{random.randint(1, 500)}",
        "status": "error" if failed else "success",
        "cause": random.choice(CAUSES) if failed else None,
    }).raise_for_status()

print("done")
