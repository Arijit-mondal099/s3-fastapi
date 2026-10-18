from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import DUMMY_HASH, hash_password, verify_password
from app.modules.auth.schemas import SignInRequest, SignUpRequest
from app.modules.users import service as users
from app.modules.users.models import User


async def sign_up(db: AsyncSession, data: SignUpRequest) -> User:
    password_hash = await run_in_threadpool(hash_password, data.password)
    return await users.create(
        db, name=data.name, email=data.email, password_hash=password_hash
    )


async def sign_in(db: AsyncSession, data: SignInRequest) -> User:
    user = await users.get_by_email(db, data.email)
    ok = await run_in_threadpool(
        verify_password, data.password, user.password_hash if user else DUMMY_HASH
    )
    if user is None or not ok:
        raise AppError(401, "Invalid email or password")  # same message for both cases
    return user
