from datetime import datetime
from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class CCEvent(Base):
    __tablename__ = "cc_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    canvas_id: Mapped[str] = mapped_column(String(64))
    step_id: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16))  # "success" or "error"
    cause: Mapped[str | None] = mapped_column(String(64))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_cc_events_lookup", "canvas_id", "step_id", "occurred_at"),
    )