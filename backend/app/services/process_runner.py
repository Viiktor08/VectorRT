import asyncio
import time
from collections.abc import AsyncIterator

from app.logging_config import logger
from app.services.errors import ProcessTimeoutError


async def run_and_collect(cmd: list[str], *, timeout_seconds: float, log_label: str) -> dict:
    """Ejecuta cmd hasta el final y devuelve el resultado completo (sin streaming)."""
    logger.info("%s iniciado cmd=%s", log_label, " ".join(cmd))
    started_at = time.monotonic()

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        logger.error("%s timeout tras %ss cmd=%s", log_label, timeout_seconds, " ".join(cmd))
        raise ProcessTimeoutError(f"{log_label} superó {timeout_seconds}s")

    duration = time.monotonic() - started_at
    logger.info(
        "%s finalizado returncode=%s duration=%.2fs", log_label, process.returncode, duration
    )

    return {
        "command": " ".join(cmd),
        "returncode": process.returncode,
        "duration_seconds": duration,
        "stdout": stdout.decode(errors="replace"),
        "stderr": stderr.decode(errors="replace"),
    }


async def stream_and_collect(
    cmd: list[str],
    *,
    timeout_seconds: float,
    log_label: str,
    result: dict | None = None,
) -> AsyncIterator[str]:
    """Ejecuta cmd cediendo cada línea de salida a medida que se produce.

    Si se pasa `result`, se rellena con command/returncode/duration_seconds
    al terminar, para que el llamador pueda persistir un resumen del job.
    """
    logger.info("%s (stream) iniciado cmd=%s", log_label, " ".join(cmd))
    started_at = time.monotonic()

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    try:
        while True:
            remaining = timeout_seconds - (time.monotonic() - started_at)
            if remaining <= 0:
                raise asyncio.TimeoutError
            line = await asyncio.wait_for(process.stdout.readline(), timeout=remaining)
            if not line:
                break
            yield line.decode(errors="replace").rstrip("\n")
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        logger.error("%s (stream) timeout tras %ss cmd=%s", log_label, timeout_seconds, " ".join(cmd))
        raise ProcessTimeoutError(f"{log_label} superó {timeout_seconds}s")
    finally:
        if process.returncode is None:
            await process.wait()

    duration = time.monotonic() - started_at
    logger.info(
        "%s (stream) finalizado returncode=%s duration=%.2fs", log_label, process.returncode, duration
    )

    if result is not None:
        result.update(
            {
                "command": " ".join(cmd),
                "returncode": process.returncode,
                "duration_seconds": duration,
            }
        )
