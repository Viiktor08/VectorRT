from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress

from app.config import MAX_LOAD_CONCURRENCY, MAX_LOAD_DURATION_SECONDS


class TargetRequest(BaseModel):
    target_ip: IPvAnyAddress


class LoadTestRequest(BaseModel):
    target_ip: IPvAnyAddress
    duration_seconds: int = Field(10, ge=1, le=MAX_LOAD_DURATION_SECONDS)
    concurrency: int = Field(10, ge=1, le=MAX_LOAD_CONCURRENCY)


class AttackResultResponse(BaseModel):
    target_ip: str
    command: str
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str


class AttackHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    attack_type: str
    target_ip: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    duration_seconds: float | None
    summary: str | None


class AttackHistoryDetail(AttackHistoryItem):
    params: dict
    raw_output: str | None
