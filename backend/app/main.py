from dotenv import load_dotenv
from fastapi import FastAPI

from app.config import ALLOWED_TARGETS
from app.logging_config import configure_logging
from app.routers import attacks

load_dotenv()
configure_logging()

app = FastAPI(title="VectorRT API")
app.include_router(attacks.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/targets")
async def list_targets() -> list:
    return ALLOWED_TARGETS
