from fastapi import APIRouter, Response

from app.api.deps import Db
from app.core.security import clear_auth_cookie, create_access_token, set_auth_cookie
from app.modules.auth import service
from app.modules.auth.schemas import SignInRequest, SignUpRequest
from app.modules.users.schemas import UserOut
from app.modules.users.service import to_user_out

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=201)
async def signup(body: SignUpRequest, response: Response, db: Db):
    user = await service.sign_up(db, body)
    set_auth_cookie(response, create_access_token(user.id))
    return to_user_out(user)


@router.post("/signin", response_model=UserOut)
async def signin(body: SignInRequest, response: Response, db: Db):
    user = await service.sign_in(db, body)
    set_auth_cookie(response, create_access_token(user.id))
    return to_user_out(user)


@router.post("/signout", status_code=204)
async def signout(response: Response):
    clear_auth_cookie(response)
