import csv
import io
import json
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _parse_csv(data: bytes) -> dict:
    try:
        text = data.decode("utf-8", errors="replace")
        reader = csv.reader(io.StringIO(text))
        headers = next(reader, [])
        row_count = sum(1 for _ in reader)
        return {"columns": headers, "row_count": row_count}
    except Exception as exc:
        logger.warning("CSV parse failed: %s", exc)
        return {}


def _parse_json(data: bytes) -> dict:
    try:
        obj = json.loads(data)
        if isinstance(obj, dict):
            return {"keys": list(obj.keys()), "type": "object"}
        if isinstance(obj, list):
            sample_keys = list(obj[0].keys()) if obj and isinstance(obj[0], dict) else []
            return {"type": "array", "length": len(obj), "sample_keys": sample_keys}
        return {"type": type(obj).__name__}
    except Exception as exc:
        logger.warning("JSON parse failed: %s", exc)
        return {}


def _parse_pdf(data: bytes) -> dict:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(data))
        return {"page_count": len(reader.pages)}
    except Exception:
        try:
            count = data.count(b"/Page ")
            return {"page_count": max(count, 1)}
        except Exception:
            return {}


def _parse_root(data: bytes, filename: str) -> dict:
    try:
        import os
        import tempfile

        import uproot
        with tempfile.NamedTemporaryFile(suffix=".root", delete=False) as f:
            f.write(data)
            tmppath = f.name
        try:
            with uproot.open(tmppath) as f:
                keys = [str(k) for k in f.keys()]
            return {"keys": keys, "format": "ROOT"}
        finally:
            os.unlink(tmppath)
    except Exception as exc:
        logger.warning("ROOT parse failed: %s", exc)
        return {"format": "ROOT"}


@celery_app.task(bind=True, name="parse_file", max_retries=3)
def parse_file(self, file_id: str, minio_key: str, content_type: str, filename: str):
    import asyncio
    from app.database import AsyncSessionLocal
    from app.models.file import File
    from app.services.storage import get_minio_client
    from app.config import settings
    from sqlalchemy import select

    try:
        client = get_minio_client()
        response = client.get_object(settings.minio_bucket, minio_key)
        data = response.read()
        response.close()
    except Exception as exc:
        logger.error("Could not fetch file %s from MinIO: %s", minio_key, exc)
        raise self.retry(exc=exc, countdown=30)

    if content_type == "text/csv" or filename.endswith(".csv"):
        metadata = _parse_csv(data)
    elif content_type == "application/json" or filename.endswith(".json"):
        metadata = _parse_json(data)
    elif content_type == "application/pdf" or filename.endswith(".pdf"):
        metadata = _parse_pdf(data)
    elif filename.endswith(".root"):
        metadata = _parse_root(data, filename)
    else:
        metadata = {"size_bytes": len(data)}

    async def _save():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(File).where(File.id == file_id))
            file_row = result.scalar_one_or_none()
            if file_row:
                file_row.parsed_metadata = metadata
                await db.commit()

    asyncio.run(_save())
    return metadata
