from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.logging_config import logger
from app.services.nmap_service import ScanTimeoutError, TargetNotAllowedError, stream_port_scan

router = APIRouter()

STREAMERS = {
    "port-scan": stream_port_scan,
}


@router.websocket("/ws/attacks/{job_id}")
async def stream_attack(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()

    attack_type = websocket.query_params.get("attack_type")
    target_ip = websocket.query_params.get("target_ip")
    streamer = STREAMERS.get(attack_type)

    if streamer is None or not target_ip:
        await websocket.send_json({"type": "error", "message": "attack_type o target_ip inválido"})
        await websocket.close()
        return

    try:
        async for line in streamer(target_ip):
            await websocket.send_json({"type": "line", "data": line})
    except (TargetNotAllowedError, ScanTimeoutError) as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
        await websocket.close()
        return
    except WebSocketDisconnect:
        logger.info("job=%s cliente desconectado durante el streaming", job_id)
        return

    await websocket.send_json({"type": "done"})
    await websocket.close()
