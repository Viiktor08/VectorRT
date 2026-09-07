from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.auth import issue_token, verify_credentials
from app.rate_limit import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login(request: Request, credentials: LoginRequest) -> LoginResponse:
    if not verify_credentials(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return LoginResponse(access_token=issue_token(credentials.username))
