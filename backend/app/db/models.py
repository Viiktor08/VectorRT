import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def _new_id() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AttackJob(Base):
    __tablename__ = "attack_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_new_id)
    attack_type: Mapped[str] = mapped_column(String, nullable=False)
    target_ip: Mapped[str] = mapped_column(String, nullable=False)
    params: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String, default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_output: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
