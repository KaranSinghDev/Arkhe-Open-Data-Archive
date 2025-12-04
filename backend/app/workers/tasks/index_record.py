import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="index_record", max_retries=3)
def index_record(self, record_id: str):
    import asyncio
    from app.database import AsyncSessionLocal
    from app.models.record import Record
    from app.services.search import index_record as search_index
    from sqlalchemy import select

    async def _run():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Record).where(Record.id == record_id))
            record = result.scalar_one_or_none()
            if record is None:
                logger.warning("index_record: record %s not found", record_id)
                return
            await search_index(record)

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.error("index_record failed for %s: %s", record_id, exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, name="deindex_record", max_retries=3)
def deindex_record(self, record_id: str):
    from app.services.search import delete_record as search_delete
    import asyncio

    try:
        asyncio.run(search_delete(record_id))
    except Exception as exc:
        logger.error("deindex_record failed for %s: %s", record_id, exc)
        raise self.retry(exc=exc, countdown=60)
