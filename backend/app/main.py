from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.routers import auth, files, records, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Zenodo-Lite API",
    version="0.1.0",
    description="A lightweight scientific data repository for physics experiments",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(search.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
