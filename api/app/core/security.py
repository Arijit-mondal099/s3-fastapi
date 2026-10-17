from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Response
from pwdlib import PasswordHash

from app.core.config import settings

ACCESS_COOKIE_NAME = "token"
_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _hasher.verify(password, hashed)


# Verified against when the email doesn't exist, so "no such user" and "wrong password"
# take the same time (prevents account enumeration by timing).
DUMMY_HASH = hash_password("not-a-real-password")


def create_access_token(user_id: object) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=settings.access_token_ttl_seconds),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )  # raises jwt.PyJWTError
    return payload["sub"]


def _cookie_opts() -> dict:
    return {
        "httponly": True,
        "secure": settings.is_prod,
        "samesite": "lax",
        "path": "/",
    }


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        token,
        max_age=settings.access_token_ttl_seconds,
        **_cookie_opts(),
    )


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE_NAME, **_cookie_opts())
