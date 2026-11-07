import json
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app import models
from app.db import Base, engine, get_db
from app.schemas import EventIn

MAX_PAYLOAD_CHARS = 4000
DEDUPE_SECONDS = 30

app = FastAPI()
Base.metadata.create_all(engine)


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