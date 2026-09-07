import asyncio

import pytest

from app.services.errors import TargetBusyError
from app.services.job_queue import is_target_busy, target_lock


@pytest.mark.asyncio
async def test_second_lock_on_same_target_is_rejected():
    async with target_lock("10.10.10.99"):
        assert is_target_busy("10.10.10.99") is True
        with pytest.raises(TargetBusyError):
            async with target_lock("10.10.10.99"):
                pass

    assert is_target_busy("10.10.10.99") is False


@pytest.mark.asyncio
async def test_lock_is_released_after_exception():
    with pytest.raises(RuntimeError):
        async with target_lock("10.10.10.98"):
            raise RuntimeError("boom")

    assert is_target_busy("10.10.10.98") is False


@pytest.mark.asyncio
async def test_different_targets_can_run_concurrently():
    async with target_lock("10.10.10.97"), target_lock("10.10.10.96"):
        assert is_target_busy("10.10.10.97") is True
        assert is_target_busy("10.10.10.96") is True
