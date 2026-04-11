from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import engine
from app.logging_config import configure_logging
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import limiter
from app.routers import auth, files, health, records, search

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    yield
    await engine.dispose()


def _cors_origins() -> list[str]:
    return [o.strip() for o in settings.backend_cors_origins.split(",") if o.strip()]


app = FastAPI(
    title="Zenodo-Lite API",
    version="1.0.0",
    description=(
        "A lightweight open-access scientific data repository for physics experiments. "
        "Supports ORCID authentication, file uploads up to 2 GB, full-text search "
        "via OpenSearch, and FAIR-compliant JSON-LD metadata on every record."
    ),
    contact={"name": "Zenodo-Lite", "url": "https://github.com/zenodo-lite/zenodo-lite"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=[
        {"name": "auth", "description": "ORCID OAuth 2.0 login and session management"},
        {"name": "records", "description": "Create, read, update, and delete research records"},
        {"name": "files", "description": "Upload and download files attached to records"},
        {"name": "search", "description": "Full-text search, facets, and autocomplete"},
    ],
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(records.router, prefix="/api", tags=["records"])
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(search.router, prefix="/api", tags=["search"])


@app.get("/health", include_in_schema=False)
async def health_legacy():
    return {"status": "ok"}
