import contextlib
import shutil
import tempfile
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

from app.config import LAB_SSH_PASSWORDS, LAB_SSH_USERNAME, is_target_allowed
from app.logging_config import logger
from app.services.errors import TargetNotAllowedError
from app.services.process_runner import run_and_collect, stream_and_collect

SSH_BRUTEFORCE_TIMEOUT_SECONDS = 60


@contextlib.contextmanager
def _lab_wordlist_file() -> Iterator[str]:
    """Escribe la wordlist fija del lab a un fichero temporal para hydra -P."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as handle:
        handle.write("\n".join(LAB_SSH_PASSWORDS) + "\n")
        path = handle.name
    try:
        yield path
    finally:
        Path(path).unlink(missing_ok=True)


def _build_ssh_bruteforce_command(target_ip: str, wordlist_path: str) -> list[str]:
    if not is_target_allowed(target_ip):
        logger.warning("ssh-bruteforce rechazado, target fuera de whitelist: %s", target_ip)
        raise TargetNotAllowedError(f"Target no permitido: {target_ip}")

    hydra_path = shutil.which("hydra")
    if hydra_path is None:
        raise RuntimeError("hydra no está instalado en este host")

    return [
        hydra_path,
        "-l", LAB_SSH_USERNAME,
        "-P", wordlist_path,
        "-t", "4",
        f"ssh://{target_ip}",
    ]


async def run_ssh_bruteforce(target_ip: str, **_params) -> dict:
    with _lab_wordlist_file() as wordlist_path:
        cmd = _build_ssh_bruteforce_command(target_ip, wordlist_path)
        result = await run_and_collect(
            cmd, timeout_seconds=SSH_BRUTEFORCE_TIMEOUT_SECONDS, log_label="ssh-bruteforce"
        )
    return {"target_ip": target_ip, **result}


async def stream_ssh_bruteforce(
    target_ip: str, *, result: dict | None = None, **_params
) -> AsyncIterator[str]:
    with _lab_wordlist_file() as wordlist_path:
        cmd = _build_ssh_bruteforce_command(target_ip, wordlist_path)
        async for line in stream_and_collect(
            cmd, timeout_seconds=SSH_BRUTEFORCE_TIMEOUT_SECONDS, log_label="ssh-bruteforce", result=result
        ):
            yield line
