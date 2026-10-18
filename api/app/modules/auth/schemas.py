from typing import Annotated

from pydantic import AfterValidator, EmailStr, Field

from app.core.schemas import CamelModel
from app.modules.users.schemas import Name

Email = Annotated[EmailStr, AfterValidator(str.lower)]


class SignUpRequest(CamelModel):
    name: Name
    email: Email
    password: str = Field(min_length=8, max_length=128)


class SignInRequest(CamelModel):
    email: Email
    password: str = Field(min_length=1, max_length=128)
