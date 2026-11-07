from datetime import datetime
from pydantic import BaseModel, Field


class EventIn(BaseModel):
    canvas_id: str
    step_id: str
    user_id: str
    endpoint: str
    payload: dict = Field(default_factory=dict)
    occurred_at: datetime | None = None
