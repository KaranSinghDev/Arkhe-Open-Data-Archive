import asyncio

import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from minio import Minio
from sqlalchemy import text

from app.config import settings
from app.database import AsyncSessionLocal

router = APIRouter(tags=["health"])


async def _check_postgres() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def _check_redis() -> bool:
    try:
        r = aioredis.from_url(settings.redis_url, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        return True
    except Exception:
        return False


def _check_minio() -> bool:
    try:
        client = Minio(
            f"{settings.minio_host}:{settings.minio_port}",
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=False,
        )
        client.bucket_exists(settings.minio_bucket)
        return True
    except Exception:
        return False


@router.get("/health/live", include_in_schema=False)
async def liveness():
    return {"status": "ok"}


@router.get("/health/ready", include_in_schema=False)
async def readiness():
    pg, redis, minio = await asyncio.gather(
        _check_postgres(),
        _check_redis(),
        asyncio.get_event_loop().run_in_executor(None, _check_minio),
    )
    checks = {"postgres": pg, "redis": redis, "minio": minio}
    healthy = all(checks.values())
    return JSONResponse(
        content={"status": "ready" if healthy else "degraded", "checks": checks},
        status_code=200 if healthy else 503,
    )
