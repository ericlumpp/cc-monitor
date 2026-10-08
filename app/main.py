from fastapi import FastAPI
from app import models  # noqa: F401  (registers the table)
from app.db import Base, engine

app = FastAPI()
Base.metadata.create_all(engine)


@app.get("/health")
def health():
    return {"status": "ok"}