import json
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlalchemy import desc, select, text
from sqlalchemy.orm import Session
from app import models
from app.anomaly import find_anomalies
from app.db import Base, engine, get_db
from app.schemas import EventIn

MAX_PAYLOAD_CHARS = 4000
DEDUPE_SECONDS = 30

app = FastAPI()
Base.metadata.create_all(engine)

DAILY_SQL = text("""
SELECT date_trunc('day', occurred_at)::date AS day, endpoint, count(*) AS failures
FROM cc_events
WHERE occurred_at > now() - make_interval(days => :days)
GROUP BY 1, 2
ORDER BY 1, 2
""")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/events", status_code=201)
def create_event(event: EventIn, response: Response, db: Session = Depends(get_db)):
    if len(json.dumps(event.payload)) > MAX_PAYLOAD_CHARS:
        raise HTTPException(413, "payload too large")

    when = event.occurred_at or datetime.now(timezone.utc)
    window = timedelta(seconds=DEDUPE_SECONDS)

    # Braze sends every failure twice. Lock on the failure's key so concurrent
    # duplicates queue up, then skip any repeat of a failure we already stored.
    key = f"{event.canvas_id}|{event.step_id}|{event.user_id}|{event.endpoint}"
    db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:k))"), {"k": key})
    existing = db.scalar(
        select(models.CCEvent.id)
        .where(
            models.CCEvent.canvas_id == event.canvas_id,
            models.CCEvent.step_id == event.step_id,
            models.CCEvent.user_id == event.user_id,
            models.CCEvent.endpoint == event.endpoint,
            models.CCEvent.occurred_at.between(when - window, when + window),
        )
        .limit(1)
    )
    if existing:
        response.status_code = 200
        return {"id": existing, "duplicate": True}

    row = models.CCEvent(**{**event.model_dump(exclude_none=True), "occurred_at": when})
    db.add(row)
    db.commit()
    return {"id": row.id}


@app.get("/stats/daily")
def daily_stats(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    rows = db.execute(DAILY_SQL, {"days": days}).all()
    return [{"day": str(r.day), "endpoint": r.endpoint, "failures": r.failures} for r in rows]


@app.get("/failures")
def failures(
    endpoint: str,
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = db.scalars(
        select(models.CCEvent)
        .where(models.CCEvent.endpoint == endpoint, models.CCEvent.occurred_at > since)
        .order_by(desc(models.CCEvent.occurred_at))
        .limit(limit)
    )
    return [
        {
            "user_id": r.user_id,
            "step_id": r.step_id,
            "payload": r.payload,
            "occurred_at": r.occurred_at.isoformat(),
        }
        for r in rows
    ]


@app.get("/anomalies")
def anomalies(db: Session = Depends(get_db)):
    return find_anomalies(db)