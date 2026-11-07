from app.anomaly import find_anomalies, format_alert
from app.db import SessionLocal

with SessionLocal() as db:
    anomalies = find_anomalies(db)

if not anomalies:
    print("No anomalies.")
for a in anomalies:
    print(format_alert(a))