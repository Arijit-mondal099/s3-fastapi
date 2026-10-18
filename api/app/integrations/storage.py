import logging
from functools import lru_cache
from uuid import uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)

AVATAR_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


@lru_cache
def get_s3():
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        config=Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=3,
            read_timeout=10,
        ),
    )


def create_avatar_upload(user_id: str, content_type: str) -> dict:
    key = f"tmp/avatars/{user_id}/{uuid4()}.{AVATAR_TYPES[content_type]}"
    post = get_s3().generate_presigned_post(
        Bucket=settings.s3_bucket,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[
            {"Content-Type": content_type},
            [
                "content-length-range",
                1,
                settings.upload_max_bytes,
            ],
        ],
        ExpiresIn=settings.presign_post_ttl,
    )
    return {"url": post["url"], "fields": post["fields"], "key": key}


def head_object(key: str) -> dict | None:
    try:
        return get_s3().head_object(Bucket=settings.s3_bucket, Key=key)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in {"404", "NoSuchKey", "NotFound"}:
            return None
        raise


def get_read_url(key: str) -> str:
    return get_s3().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=settings.presign_get_ttl,
    )


def delete_object_quietly(key: str) -> None:
    try:
        get_s3().delete_object(Bucket=settings.s3_bucket, Key=key)
    except (ClientError, BotoCoreError):
        logger.exception("S3 cleanup failed for key=%s", key)
