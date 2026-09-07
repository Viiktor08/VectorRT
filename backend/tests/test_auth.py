import time

import jwt
import pytest

from app.auth import (
    AUTH_PASSWORD,
    AUTH_USERNAME,
    JWT_ALGORITHM,
    SECRET_KEY,
    AuthError,
    decode_token,
    issue_token,
    verify_credentials,
)


def test_correct_credentials_are_accepted():
    assert verify_credentials(AUTH_USERNAME, AUTH_PASSWORD) is True


def test_wrong_password_is_rejected():
    assert verify_credentials(AUTH_USERNAME, "not-the-password") is False


def test_wrong_username_is_rejected():
    assert verify_credentials("not-the-user", AUTH_PASSWORD) is False


def test_issued_token_roundtrips_to_username():
    token = issue_token("someone")
    assert decode_token(token) == "someone"


def test_tampered_token_is_rejected():
    token = issue_token("someone") + "x"
    with pytest.raises(AuthError):
        decode_token(token)


def test_expired_token_is_rejected():
    now = int(time.time())
    expired = jwt.encode(
        {"sub": "someone", "iat": now - 100, "exp": now - 1}, SECRET_KEY, algorithm=JWT_ALGORITHM
    )
    with pytest.raises(AuthError):
        decode_token(expired)
