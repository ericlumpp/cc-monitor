from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class EventIn(BaseModel):
    canvas_id: str
    step_id: str
    user_id: str
    status: Literal["success", "error"]
    cause: str | None = None
    occurred_at: datetime | None = None
