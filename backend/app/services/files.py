import mimetypes
from uuid import UUID, uuid4

from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.services import storage

_MAX_FILE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB
_ALLOWED_TYPES = {
    "text/csv",
    "application/json",
    "application/pdf",
    "application/octet-stream",
    "text/plain",
    "application/zip",
    "application/x-tar",
    "application/gzip",
}


def _detect_content_type(filename: str, declared: str) -> str:
    if declared and declared != "application/octet-stream":
        return declared
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"


async def upload_file(
    db: AsyncSession,
    record_id: UUID,
    upload: UploadFile,
) -> File:
    data = await upload.read()
    size = len(data)

    if size > _MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 2 GB limit",
        )

    content_type = _detect_content_type(upload.filename or "", upload.content_type or "")
    object_key = storage.build_object_key(str(record_id), upload.filename or "upload")

    await storage.upload_file(object_key, data, content_type)

    file_row = File(
        id=uuid4(),
        record_id=record_id,
        filename=upload.filename or "upload",
        content_type=content_type,
        size_bytes=size,
        minio_key=object_key,
    )
    db.add(file_row)
    await db.commit()
    await db.refresh(file_row)
    return file_row


async def list_files(db: AsyncSession, record_id: UUID) -> tuple[list[File], int]:
    q = select(File).where(File.record_id == record_id)
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()
    files = (await db.execute(q)).scalars().all()
    return list(files), total


async def get_file(db: AsyncSession, file_id: UUID) -> File | None:
    result = await db.execute(select(File).where(File.id == file_id))
    return result.scalar_one_or_none()


async def delete_file(db: AsyncSession, file_row: File) -> None:
    storage.delete_file(file_row.minio_key)
    await db.delete(file_row)
    await db.commit()
