from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "production", "test"] = "development"
    client_url: str
    database_url: str
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_ttl_seconds: int = 60 * 60 * 24 * 7

    aws_region: str
    s3_bucket: str
    upload_max_bytes: int = 2 * 1024 * 1024
    presign_post_ttl: int = 60
    presign_get_ttl: int = 3600

    @property
    def is_prod(self) -> bool:
        return self.environment == "production"


settings = Settings()  # type: ignore
