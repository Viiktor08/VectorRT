import os
import secrets
import time

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.logging_config import logger

AUTH_USERNAME = os.getenv("VECTORRT_USERNAME", "admin")
AUTH_PASSWORD = os.getenv("VECTORRT_PASSWORD", "changeme")
SECRET_KEY = os.getenv("VECTORRT_SECRET_KEY", "dev-secret-change-me")
TOKEN_TTL_SECONDS = 8 * 60 * 60  # 8h: sesión de trabajo, no un token eterno
JWT_ALGORITHM = "HS256"

if AUTH_PASSWORD == "changeme" or SECRET_KEY == "dev-secret-change-me":  # noqa: S105
    logger.warning(
        "Usando credenciales/clave de firma por defecto. "
        "Define VECTORRT_USERNAME, VECTORRT_PASSWORD y VECTORRT_SECRET_KEY antes de exponer esto fuera de tu máquina."
    )

_bearer_scheme = HTTPBearer(auto_error=False)


class AuthError(Exception):
    pass


def verify_credentials(username: str, password: str) -> bool:
    # Comparación en tiempo constante: evita filtrar por timing si el usuario/contraseña coincide parcialmente.
    return secrets.compare_digest(username, AUTH_USERNAME) and secrets.compare_digest(
        password, AUTH_PASSWORD
    )


def issue_token(username: str) -> str:
    now = int(time.time())
    payload = {"sub": username, "iat": now, "exp": now + TOKEN_TTL_SECONDS}
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise AuthError("Token inválido o caducado") from exc
    return payload["sub"]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Falta el token de autenticación")
    try:
        return decode_token(credentials.credentials)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def get_user_from_ws_token(token: str | None) -> str:
    if not token:
        raise AuthError("Falta el token de autenticación")
    return decode_token(token)
