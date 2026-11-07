import json

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.db import Base, engine, get_db
from app.schemas import EventIn

MAX_PAYLOAD_CHARS = 4000

app = FastAPI()
Base.metadata.create_all(engine)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/events", status_code=201)
def create_event(event: EventIn, db: Session = Depends(get_db)):
    if len(json.dumps(event.payload)) > MAX_PAYLOAD_CHARS:
        raise HTTPException(413, "payload too large")
    row = models.CCEvent(**event.model_dump(exclude_none=True))
    db.add(row)
    db.commit()
    return {"id": row.id}
