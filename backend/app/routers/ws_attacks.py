from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.logging_config import logger
from app.models.attacks import LoadTestRequest, TargetRequest
from app.services import attack_runner
from app.services.errors import (
    InvalidAttackParamsError,
    ProcessTimeoutError,
    TargetBusyError,
    TargetNotAllowedError,
)

router = APIRouter()

VALID_ATTACK_TYPES = {"port-scan", "ssh-bruteforce", "load-test"}


def _parse_params(attack_type: str, query_params) -> dict:
    target_ip = query_params.get("target_ip")
    if not target_ip:
        raise InvalidAttackParamsError("target_ip requerido")

    if attack_type == "load-test":
        request = LoadTestRequest(
            target_ip=target_ip,
            duration_seconds=query_params.get("duration_seconds", 10),
            concurrency=query_params.get("concurrency", 10),
        )
        return {
            "target_ip": str(request.target_ip),
            "duration_seconds": request.duration_seconds,
            "concurrency": request.concurrency,
        }

    request = TargetRequest(target_ip=target_ip)
    return {"target_ip": str(request.target_ip)}


@router.websocket("/ws/attacks/{job_id}")
async def stream_attack(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()

    attack_type = websocket.query_params.get("attack_type")
    if attack_type not in VALID_ATTACK_TYPES:
        await websocket.send_json({"type": "error", "message": f"attack_type inválido: {attack_type}"})
        await websocket.close()
        return

    try:
        params = _parse_params(attack_type, websocket.query_params)
    except (InvalidAttackParamsError, ValueError) as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
        await websocket.close()
        return

    target_ip = params.pop("target_ip")

    try:
        async for line in attack_runner.stream_attack(attack_type, target_ip, **params):
            await websocket.send_json({"type": "line", "data": line})
    except (TargetNotAllowedError, ProcessTimeoutError, TargetBusyError, InvalidAttackParamsError) as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
        await websocket.close()
        return
    except WebSocketDisconnect:
        logger.info("job=%s cliente desconectado durante el streaming", job_id)
        return

    await websocket.send_json({"type": "done"})
    await websocket.close()
