import shutil
from collections.abc import AsyncIterator

from app.config import is_target_allowed
from app.logging_config import logger
from app.services.errors import TargetNotAllowedError
from app.services.process_runner import run_and_collect, stream_and_collect

PORT_SCAN_TIMEOUT_SECONDS = 60


def _build_port_scan_command(target_ip: str) -> list[str]:
    if not is_target_allowed(target_ip):
        logger.warning("port-scan rechazado, target fuera de whitelist: %s", target_ip)
        raise TargetNotAllowedError(f"Target no permitido: {target_ip}")

    nmap_path = shutil.which("nmap")
    if nmap_path is None:
        raise RuntimeError("nmap no está instalado en este host")

    # Flags fijos: el usuario nunca puede inyectar flags arbitrarios de nmap.
    return [nmap_path, "-sV", "-p", "1-1000", target_ip]


async def run_port_scan(target_ip: str, **_params) -> dict:
    cmd = _build_port_scan_command(target_ip)
    result = await run_and_collect(cmd, timeout_seconds=PORT_SCAN_TIMEOUT_SECONDS, log_label="port-scan")
    return {"target_ip": target_ip, **result}


def stream_port_scan(target_ip: str, *, result: dict | None = None, **_params) -> AsyncIterator[str]:
    cmd = _build_port_scan_command(target_ip)
    return stream_and_collect(cmd, timeout_seconds=PORT_SCAN_TIMEOUT_SECONDS, log_label="port-scan", result=result)
