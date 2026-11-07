from datetime import datetime
from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class CCEvent(Base):
    """One row per failed Connected Content call."""
    __tablename__ = "cc_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    canvas_id: Mapped[str] = mapped_column(String(64))
    step_id: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[str] = mapped_column(String(64))
    endpoint: Mapped[str] = mapped_column(String(256))
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("ix_cc_events_endpoint_time", "endpoint", "occurred_at"),)
