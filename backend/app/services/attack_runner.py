from collections.abc import AsyncIterator
from datetime import datetime, timezone

from app.db import SessionLocal
from app.db.models import AttackJob
from app.services import hydra_service, load_service, nmap_service
from app.services.errors import InvalidAttackParamsError
from app.services.job_queue import target_lock

RUNNERS = {
    "port-scan": nmap_service.run_port_scan,
    "ssh-bruteforce": hydra_service.run_ssh_bruteforce,
    "load-test": load_service.run_load_test,
}

STREAMERS = {
    "port-scan": nmap_service.stream_port_scan,
    "ssh-bruteforce": hydra_service.stream_ssh_bruteforce,
    "load-test": load_service.stream_load_test,
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def run_attack(attack_type: str, target_ip: str, **params) -> dict:
    """Ejecuta un ataque completo (sin streaming), con lock por target y job en DB."""
    runner = RUNNERS.get(attack_type)
    if runner is None:
        raise InvalidAttackParamsError(f"Tipo de ataque desconocido: {attack_type}")

    async with target_lock(target_ip):
        db = SessionLocal()
        job = AttackJob(attack_type=attack_type, target_ip=target_ip, params=params, status="running")
        db.add(job)
        db.commit()

        try:
            result = await runner(target_ip, **params)
        except Exception as exc:
            job.status = "error"
            job.summary = str(exc)
            job.finished_at = _utcnow()
            db.commit()
            db.close()
            raise

        job.status = "success" if result.get("returncode") == 0 else "error"
        job.duration_seconds = result.get("duration_seconds")
        job.raw_output = (result.get("stdout") or "") + (result.get("stderr") or "")
        job.summary = f"returncode={result.get('returncode')}"
        job.finished_at = _utcnow()
        db.commit()
        db.close()

    return result


async def stream_attack(attack_type: str, target_ip: str, **params) -> AsyncIterator[str]:
    """Ejecuta un ataque cediendo líneas en vivo, con lock por target y job en DB."""
    streamer = STREAMERS.get(attack_type)
    if streamer is None:
        raise InvalidAttackParamsError(f"Tipo de ataque desconocido: {attack_type}")

    async with target_lock(target_ip):
        db = SessionLocal()
        job = AttackJob(attack_type=attack_type, target_ip=target_ip, params=params, status="running")
        db.add(job)
        db.commit()

        lines: list[str] = []
        result: dict = {}
        try:
            async for line in streamer(target_ip, result=result, **params):
                lines.append(line)
                yield line
        except Exception as exc:
            job.status = "error"
            job.summary = str(exc)
            job.raw_output = "\n".join(lines)
            job.finished_at = _utcnow()
            db.commit()
            db.close()
            raise

        job.status = "success" if result.get("returncode") == 0 else "error"
        job.duration_seconds = result.get("duration_seconds")
        job.raw_output = "\n".join(lines)
        job.summary = f"returncode={result.get('returncode')}"
        job.finished_at = _utcnow()
        db.commit()
        db.close()
