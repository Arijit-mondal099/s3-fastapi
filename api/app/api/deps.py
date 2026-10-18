import uuid
from typing import Annotated

import jwt
from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import ACCESS_COOKIE_NAME, decode_access_token
from app.db.session import get_db
from app.modules.users import service as users_service
from app.modules.users.models import User

Db = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: Db, token: Annotated[str | None, Cookie(alias=ACCESS_COOKIE_NAME)] = None
) -> User:
    if not token:
        raise AppError(401, "Not authenticated")
    try:
        user_id = uuid.UUID(decode_access_token(token))
    except (jwt.PyJWTError, ValueError):
        raise AppError(401, "Invalid or expired session") from None
    user = await users_service.get_by_id(db, user_id)
    if user is None:
        raise AppError(401, "Account no longer exists")  # valid token, deleted user
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
