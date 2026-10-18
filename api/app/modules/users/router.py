from fastapi import APIRouter, Response

from app.api.deps import CurrentUser, Db
from app.core.security import clear_auth_cookie
from app.integrations import storage
from app.modules.users import service
from app.modules.users.schemas import (
    AvatarConfirmRequest,
    AvatarPresignRequest,
    AvatarPresignResponse,
    UpdateProfileRequest,
    UserOut,
)

router = APIRouter(prefix="/users/me", tags=["users"])


@router.get("", response_model=UserOut)
async def get_me(user: CurrentUser):
    return service.to_user_out(user)


@router.patch("", response_model=UserOut)
async def update_me(body: UpdateProfileRequest, user: CurrentUser, db: Db):
    user = await service.update_profile(db, user, body.model_dump(exclude_unset=True))
    return service.to_user_out(user)


@router.delete("", status_code=204)
async def delete_me(response: Response, user: CurrentUser, db: Db):
    await service.delete_account(db, user)
    clear_auth_cookie(response)


@router.post("/avatar/presign", response_model=AvatarPresignResponse)
async def presign_avatar(body: AvatarPresignRequest, user: CurrentUser):
    return storage.create_avatar_upload(str(user.id), body.content_type)


@router.put("/avatar", response_model=UserOut)
async def confirm_avatar(body: AvatarConfirmRequest, user: CurrentUser, db: Db):
    return service.to_user_out(await service.set_avatar(db, user, body.key))


@router.delete("/avatar", response_model=UserOut)
async def delete_avatar(user: CurrentUser, db: Db):
    return service.to_user_out(await service.remove_avatar(db, user))
