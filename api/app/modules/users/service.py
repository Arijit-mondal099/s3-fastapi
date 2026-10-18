import uuid

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.integrations import storage
from app.modules.users.models import User
from app.modules.users.schemas import UserOut


def to_user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        bio=user.bio,
        avatar_url=storage.get_read_url(user.avatar_key) if user.avatar_key else None,
        created_at=user.created_at,
    )


async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.get(User, user_id)


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    return (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()


async def create(
    db: AsyncSession, *, name: str, email: str, password_hash: str
) -> User:
    user = User(name=name, email=email, password_hash=password_hash)
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppError(409, "Email already in use") from None
    return user


async def update_profile(db: AsyncSession, user: User, data: dict) -> User:
    for field, value in data.items():
        setattr(user, field, value)
    await db.commit()
    return user


async def set_avatar(db: AsyncSession, user: User, key: str) -> User:
    if not key.startswith(f"tmp/avatars/{user.id}/"):
        raise AppError(403, "Invalid file key")

    meta = await run_in_threadpool(storage.head_object, key)
    if meta is None:
        raise AppError(400, "File not found. Upload it first.")

    if (
        meta["ContentLength"] > settings.upload_max_bytes
        or meta.get("ContentType") not in storage.AVATAR_TYPES
    ):
        await run_in_threadpool(storage.delete_object_quietly, key)
        raise AppError(400, "Invalid file")

    old_key = user.avatar_key
    user.avatar_key = key
    await db.commit()

    if old_key and old_key != key:
        await run_in_threadpool(storage.delete_object_quietly, old_key)

    return user


async def remove_avatar(db: AsyncSession, user: User) -> User:
    old_key = user.avatar_key
    if old_key:
        user.avatar_key = None
        await db.commit()
        await run_in_threadpool(storage.delete_object_quietly, old_key)
    return user


async def delete_account(db: AsyncSession, user: User) -> None:
    old_key = user.avatar_key
    await db.delete(user)
    await db.commit()
    if old_key:
        await run_in_threadpool(storage.delete_object_quietly, old_key)
