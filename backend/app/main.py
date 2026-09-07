from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.auth import get_current_user
from app.config import ALLOWED_TARGETS
from app.db import SessionLocal, init_db
from app.logging_config import configure_logging, logger
from app.rate_limit import limiter
from app.routers import attacks, auth, ws_attacks

load_dotenv()
configure_logging()
init_db()

app = FastAPI(title="VectorRT API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth.router)
app.include_router(attacks.router)
app.include_router(ws_attacks.router)


@app.get("/health")
async def health() -> dict:
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception:
        logger.exception("health check: fallo de conexión a la base de datos")
        db_ok = False

    return {"status": "ok" if db_ok else "degraded", "db": db_ok}


@app.get("/api/targets")
async def list_targets(_user: str = Depends(get_current_user)) -> list:
    return ALLOWED_TARGETS
