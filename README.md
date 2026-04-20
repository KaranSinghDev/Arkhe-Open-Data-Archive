# Zenodo-Lite

A lightweight open-access scientific data repository for physics experiments, inspired by [Zenodo](https://zenodo.org). Researchers can upload datasets, software, and simulation outputs, assign persistent identifiers, and make their work discoverable by the global research community — entirely free using their ORCID account.

## Features

- **ORCID authentication** — sign in with a free [orcid.org](https://orcid.org) account; no new credentials required
- **File uploads up to 2 GB** — supports CSV, JSON, PDF, ROOT, and other common research formats
- **Full-text search** — powered by OpenSearch with facets (experiment, type, year) and autocomplete
- **FAIR-compliant metadata** — every record exposes a `GET /records/{id}/metadata.json` endpoint returning schema.org JSON-LD (`application/ld+json`)
- **Background file parsing** — Celery workers extract metadata from CSV, JSON, PDF, and ROOT (uproot) files automatically after upload
- **Presigned download URLs** — files are served via MinIO presigned URLs; no credentials needed to download public records
- **Prometheus metrics** — instrumented at `/metrics` for production monitoring

## Architecture

```
Browser → Nginx (port 80)
             ├── /api/*  → FastAPI (port 8000)
             │                ├── PostgreSQL (records, users, files)
             │                ├── MinIO (file blobs)
             │                ├── OpenSearch (full-text index)
             │                └── Redis ← Celery workers
             └── /*      → React SPA (static build)
```

## Quick start

**Prerequisites:** Docker and Docker Compose.

```bash
cp .env.example .env
# Edit .env — set ORCID_CLIENT_ID, ORCID_CLIENT_SECRET, SECRET_KEY at minimum
docker compose up --build
```

Open [http://localhost](http://localhost). The API docs are at [http://localhost/api/docs](http://localhost/api/docs).

## Development

```bash
# Backend (Python 3.12+)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload          # http://localhost:8000

# Frontend (Node 20+)
cd frontend
npm install
npm run dev                             # http://localhost:5173
```

Run tests:

```bash
cd backend && pytest -x -q
```

## Configuration

All configuration is via environment variables (see `.env.example`).

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL async URL (`postgresql+asyncpg://...`) |
| `REDIS_URL` | Redis URL for Celery broker/backend |
| `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` | MinIO credentials |
| `SECRET_KEY` | JWT signing secret (change in production!) |
| `ORCID_CLIENT_ID` / `ORCID_CLIENT_SECRET` | From [orcid.org/developer-tools](https://orcid.org/developer-tools) |
| `ORCID_REDIRECT_URI` | Must match the redirect registered with ORCID |

## Production deployment

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

The prod override disables hot-reload, uses 4 Uvicorn workers, and adds memory/CPU limits.

## License

MIT — see [LICENSE](LICENSE).
