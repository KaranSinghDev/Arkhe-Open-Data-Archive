from celery import Celery
from app.config import settings

celery_app = Celery(
    "zenodo_lite",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks.parse_file", "app.workers.tasks.index_record"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
