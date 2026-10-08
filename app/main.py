from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.db import Base, engine, get_db
from app.schemas import EventIn

app = FastAPI()
Base.metadata.create_all(engine)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/events", status_code=201)
def create_event(event: EventIn, db: Session = Depends(get_db)):
    if event.status == "error" and not event.cause:
        raise HTTPException(422, "error events need a cause")
    row = models.CCEvent(**event.model_dump(exclude_none=True))
    db.add(row)
    db.commit()
    return {"id": row.id}
