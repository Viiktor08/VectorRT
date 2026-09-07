from contextlib import contextmanager

from fastapi import APIRouter, HTTPException

from app.db import SessionLocal
from app.db.models import AttackJob
from app.models.attacks import (
    AttackHistoryDetail,
    AttackHistoryItem,
    AttackResultResponse,
    LoadTestRequest,
    TargetRequest,
)
from app.services import attack_runner
from app.services.errors import (
    InvalidAttackParamsError,
    ProcessTimeoutError,
    TargetBusyError,
    TargetNotAllowedError,
)

router = APIRouter(prefix="/api/attacks", tags=["attacks"])


@contextmanager
def _translate_attack_errors():
    try:
        yield
    except TargetNotAllowedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except TargetBusyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ProcessTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except InvalidAttackParamsError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/port-scan", response_model=AttackResultResponse)
async def port_scan(request: TargetRequest) -> AttackResultResponse:
    with _translate_attack_errors():
        result = await attack_runner.run_attack("port-scan", str(request.target_ip))
    return AttackResultResponse(**result)


@router.post("/ssh-bruteforce", response_model=AttackResultResponse)
async def ssh_bruteforce(request: TargetRequest) -> AttackResultResponse:
    with _translate_attack_errors():
        result = await attack_runner.run_attack("ssh-bruteforce", str(request.target_ip))
    return AttackResultResponse(**result)


@router.post("/load-test", response_model=AttackResultResponse)
async def load_test(request: LoadTestRequest) -> AttackResultResponse:
    with _translate_attack_errors():
        result = await attack_runner.run_attack(
            "load-test",
            str(request.target_ip),
            duration_seconds=request.duration_seconds,
            concurrency=request.concurrency,
        )
    return AttackResultResponse(**result)


@router.get("/history", response_model=list[AttackHistoryItem])
async def attack_history(
    target_ip: str | None = None, attack_type: str | None = None
) -> list[AttackHistoryItem]:
    db = SessionLocal()
    try:
        query = db.query(AttackJob).order_by(AttackJob.started_at.desc())
        if target_ip:
            query = query.filter(AttackJob.target_ip == target_ip)
        if attack_type:
            query = query.filter(AttackJob.attack_type == attack_type)
        jobs = query.limit(100).all()
        return [AttackHistoryItem.model_validate(job) for job in jobs]
    finally:
        db.close()


@router.get("/history/{job_id}", response_model=AttackHistoryDetail)
async def attack_history_detail(job_id: str) -> AttackHistoryDetail:
    db = SessionLocal()
    try:
        job = db.get(AttackJob, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"Job no encontrado: {job_id}")
        return AttackHistoryDetail.model_validate(job)
    finally:
        db.close()
