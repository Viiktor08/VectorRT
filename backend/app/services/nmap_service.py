import asyncio
import shutil
import time
from collections.abc import AsyncIterator

from app.config import is_target_allowed
from app.logging_config import logger

PORT_SCAN_TIMEOUT_SECONDS = 60


class TargetNotAllowedError(Exception):
    pass


class ScanTimeoutError(Exception):
    pass


def _build_port_scan_command(target_ip: str) -> list[str]:
    if not is_target_allowed(target_ip):
        logger.warning("port-scan rechazado, target fuera de whitelist: %s", target_ip)
        raise TargetNotAllowedError(f"Target no permitido: {target_ip}")

    nmap_path = shutil.which("nmap")
    if nmap_path is None:
        raise RuntimeError("nmap no está instalado en este host")

    # Flags fijos: el usuario nunca puede inyectar flags arbitrarios de nmap.
    return [nmap_path, "-sV", "-p", "1-1000", target_ip]


async def run_port_scan(target_ip: str) -> dict:
    cmd = _build_port_scan_command(target_ip)

    logger.info("port-scan iniciado target=%s cmd=%s", target_ip, " ".join(cmd))
    started_at = time.monotonic()

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=PORT_SCAN_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        logger.error("port-scan timeout target=%s tras %ss", target_ip, PORT_SCAN_TIMEOUT_SECONDS)
        raise ScanTimeoutError(f"Escaneo de {target_ip} superó {PORT_SCAN_TIMEOUT_SECONDS}s")

    duration = time.monotonic() - started_at
    logger.info(
        "port-scan finalizado target=%s returncode=%s duration=%.2fs",
        target_ip,
        process.returncode,
        duration,
    )

    return {
        "target_ip": target_ip,
        "command": " ".join(cmd),
        "returncode": process.returncode,
        "duration_seconds": duration,
        "stdout": stdout.decode(errors="replace"),
        "stderr": stderr.decode(errors="replace"),
    }


async def stream_port_scan(target_ip: str) -> AsyncIterator[str]:
    """Ejecuta el escaneo y va cediendo cada línea de salida a medida que nmap la produce."""
    cmd = _build_port_scan_command(target_ip)

    logger.info("port-scan (stream) iniciado target=%s cmd=%s", target_ip, " ".join(cmd))
    started_at = time.monotonic()

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    try:
        while True:
            remaining = PORT_SCAN_TIMEOUT_SECONDS - (time.monotonic() - started_at)
            if remaining <= 0:
                raise asyncio.TimeoutError
            line = await asyncio.wait_for(process.stdout.readline(), timeout=remaining)
            if not line:
                break
            yield line.decode(errors="replace").rstrip("\n")
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        logger.error("port-scan (stream) timeout target=%s tras %ss", target_ip, PORT_SCAN_TIMEOUT_SECONDS)
        raise ScanTimeoutError(f"Escaneo de {target_ip} superó {PORT_SCAN_TIMEOUT_SECONDS}s")
    finally:
        if process.returncode is None:
            await process.wait()

    duration = time.monotonic() - started_at
    logger.info(
        "port-scan (stream) finalizado target=%s returncode=%s duration=%.2fs",
        target_ip,
        process.returncode,
        duration,
    )
