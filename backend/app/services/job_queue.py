import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.services.errors import TargetBusyError

_busy_targets: set[str] = set()
_lock = asyncio.Lock()


@asynccontextmanager
async def target_lock(target_ip: str) -> AsyncIterator[None]:
    """Evita que dos ataques corran a la vez contra el mismo target."""
    async with _lock:
        if target_ip in _busy_targets:
            raise TargetBusyError(f"Ya hay un ataque en curso contra {target_ip}")
        _busy_targets.add(target_ip)
    try:
        yield
    finally:
        async with _lock:
            _busy_targets.discard(target_ip)


def is_target_busy(target_ip: str) -> bool:
    return target_ip in _busy_targets
