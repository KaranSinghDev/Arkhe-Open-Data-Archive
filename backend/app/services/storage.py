import io
from typing import AsyncIterator

from minio import Minio
from minio.error import S3Error

from app.config import settings

_client: Minio | None = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            f"{settings.minio_host}:{settings.minio_port}",
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=False,
        )
    return _client


async def upload_file(
    object_key: str,
    data: bytes,
    content_type: str,
) -> int:
    client = get_minio_client()
    size = len(data)
    client.put_object(
        settings.minio_bucket,
        object_key,
        io.BytesIO(data),
        length=size,
        content_type=content_type,
    )
    return size


def get_presigned_download_url(object_key: str, expires_seconds: int = 3600) -> str:
    from datetime import timedelta
    client = get_minio_client()
    return client.presigned_get_object(
        settings.minio_bucket,
        object_key,
        expires=timedelta(seconds=expires_seconds),
    )


def delete_file(object_key: str) -> None:
    client = get_minio_client()
    try:
        client.remove_object(settings.minio_bucket, object_key)
    except S3Error:
        pass


def build_object_key(record_id: str, filename: str) -> str:
    safe_name = filename.replace(" ", "_")
    return f"records/{record_id}/{safe_name}"
