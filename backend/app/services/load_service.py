import shutil
from collections.abc import AsyncIterator

from app.config import LOAD_TEST_TARGETS, MAX_LOAD_CONCURRENCY, MAX_LOAD_DURATION_SECONDS, is_load_test_target_allowed
from app.logging_config import logger
from app.services.errors import InvalidAttackParamsError, TargetNotAllowedError
from app.services.process_runner import run_and_collect, stream_and_collect

# Margen sobre la duración pedida para que el proceso siege tenga tiempo de
# cerrar limpio antes de que nuestro propio timeout lo mate en seco.
LOAD_TEST_TIMEOUT_MARGIN_SECONDS = 15


def _build_load_test_command(target_ip: str, duration_seconds: int, concurrency: int) -> list[str]:
    if not is_load_test_target_allowed(target_ip):
        logger.warning("load-test rechazado, target sin servicio HTTP en whitelist: %s", target_ip)
        raise TargetNotAllowedError(f"Target no permitido para carga/DDoS: {target_ip}")

    if not (1 <= duration_seconds <= MAX_LOAD_DURATION_SECONDS):
        raise InvalidAttackParamsError(f"duration_seconds debe estar entre 1 y {MAX_LOAD_DURATION_SECONDS}")
    if not (1 <= concurrency <= MAX_LOAD_CONCURRENCY):
        raise InvalidAttackParamsError(f"concurrency debe estar entre 1 y {MAX_LOAD_CONCURRENCY}")

    siege_path = shutil.which("siege")
    if siege_path is None:
        raise RuntimeError("siege no está instalado en este host")

    target = LOAD_TEST_TARGETS[target_ip]
    url = f"http://{target_ip}:{target['port']}{target['path']}"

    return [
        siege_path,
        "-b",  # benchmark: sin delay entre peticiones
        "-j",  # solo el resumen final, como JSON (nada de una línea por petición)
        "-c", str(concurrency),
        "-t", f"{duration_seconds}S",
        url,
    ]


def _timeout_for(duration_seconds: int) -> float:
    return duration_seconds + LOAD_TEST_TIMEOUT_MARGIN_SECONDS


async def run_load_test(target_ip: str, *, duration_seconds: int, concurrency: int, **_params) -> dict:
    cmd = _build_load_test_command(target_ip, duration_seconds, concurrency)
    result = await run_and_collect(
        cmd, timeout_seconds=_timeout_for(duration_seconds), log_label="load-test"
    )
    return {"target_ip": target_ip, **result}


async def stream_load_test(
    target_ip: str, *, duration_seconds: int, concurrency: int, result: dict | None = None, **_params
) -> AsyncIterator[str]:
    cmd = _build_load_test_command(target_ip, duration_seconds, concurrency)
    async for line in stream_and_collect(
        cmd, timeout_seconds=_timeout_for(duration_seconds), log_label="load-test", result=result
    ):
        yield line
