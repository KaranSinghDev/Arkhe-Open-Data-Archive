# Arkhe

*From the Greek ἀρχή — origin, beginning, source.*

A self-hostable, lightweight scientific data repository built for research groups, university departments, and teaching environments that need FAIR-compliant data sharing without the operational overhead of a full-scale platform.

---

## Background

[Zenodo](https://zenodo.org) is a great platform — it lets researchers publish datasets, software, and papers with a permanent DOI, completely free. I use it and think it does its job well. [InvenioRDM](https://inveniosoftware.org/products/rdm/) is the open-source software that powers it, and it is a serious, well-maintained system built by a team at CERN.

The problem I kept running into is that neither is easy to self-host. InvenioRDM requires Kubernetes or a complex Docker setup, at least 16 GB of RAM, and a fair amount of configuration just to get a first record in. I went through their documentation, looked at GitHub issues, and read threads in communities like the HEP Software Foundation — and the same question kept coming up: *is there something simpler, that I can just run on my own server?*

The situations people described were practical ones:

- A university department that wants its own repository for student work, without sending data to an external service
- A research group that can't upload pre-publication data to CERN-operated infrastructure due to compliance rules
- A summer school or workshop where participants need to share datasets and code for a few weeks
- A lab that works in a restricted or offline network environment

I built Arkhe to cover that gap — something that works like Zenodo for a small group, runs with a single `docker compose up`, and doesn't need a dedicated sysadmin to maintain.

---

## What it does

- **ORCID authentication** — researchers sign in with their existing [orcid.org](https://orcid.org) identity; no new accounts or passwords
- **File upload up to 2 GB** — CSV, JSON, PDF, HDF5, and ROOT (uproot) files supported; metadata extracted automatically in the background
- **Full-text search** — OpenSearch-backed with facets (experiment, record type, year) and prefix autocomplete
- **FAIR-compliant metadata** — every record has a `GET /records/{id}/metadata.json` endpoint returning schema.org `Dataset` JSON-LD (`application/ld+json`)
- **Presigned download URLs** — public files downloadable without credentials via MinIO presigned URLs
- **Background processing** — Celery workers handle file parsing and search indexing asynchronously so uploads return immediately
- **Observability** — structured JSON logs (structlog), Prometheus metrics at `/metrics`, and deep health checks at `/health/ready`

---

## Architecture

```
Browser
  └── Nginx :80
        ├── /api/*  ──► FastAPI (uvicorn)
        │                  ├── PostgreSQL  — users, records, file metadata
        │                  ├── MinIO       — file blobs (S3-compatible)
        │                  ├── OpenSearch  — full-text search index
        │                  └── Redis  ◄──  Celery workers
        │                                   (file parsing, index updates)
        └── /*      ──► React SPA (static, built into nginx image)
```

Nine services total, all defined in `docker-compose.yml`. The nginx image is a multi-stage build that compiles the React frontend and copies the static output — no separate frontend container at runtime.

---

## Quick start

**Prerequisites:** Docker and Docker Compose (v2).

### Option A — pre-built images (recommended)

No git clone or build step required.

```bash
curl -O https://raw.githubusercontent.com/KaranSinghDev/Arkhe-Open-Data-Archive/main/docker-compose.hub.yml
curl -O https://raw.githubusercontent.com/KaranSinghDev/Arkhe-Open-Data-Archive/main/.env.example
cp .env.example .env
# Edit .env — set ORCID_CLIENT_ID, ORCID_CLIENT_SECRET, SECRET_KEY,
#             POSTGRES_PASSWORD, MINIO_ROOT_PASSWORD, ORCID_REDIRECT_URI
docker compose -f docker-compose.hub.yml up -d
```

### Option B — build from source

```bash
git clone https://github.com/KaranSinghDev/Arkhe-Open-Data-Archive.git
cd arkhe
cp .env.example .env
docker compose up --build
```

Open [http://localhost](http://localhost). API docs: [http://localhost/api/docs](http://localhost/api/docs).

Register a free ORCID Public API at [orcid.org/developer-tools](https://orcid.org/developer-tools). Set the redirect URI to `http://localhost/auth/callback` (or your domain).

---

## Development setup

```bash
# Backend — Python 3.12+
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload        # http://localhost:8000

# Frontend — Node 20+
cd frontend
npm install
npm run dev                          # http://localhost:5173 (proxies /api to :8000)
```

```bash
# Tests
cd backend && pytest -x -q

# Lint
cd backend && ruff check app/
cd frontend && npx tsc --noEmit
```

---

## Configuration

All settings are environment variables. Copy `.env.example` and edit.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://user:pass@postgres:5432/db` |
| `SECRET_KEY` | Yes | JWT signing secret — use a long random string |
| `ORCID_CLIENT_ID` | Yes | From orcid.org/developer-tools |
| `ORCID_CLIENT_SECRET` | Yes | From orcid.org/developer-tools |
| `ORCID_REDIRECT_URI` | Yes | Must match what ORCID has on record |
| `REDIS_URL` | No | Default: `redis://redis:6379/0` |
| `MINIO_ROOT_USER` / `_PASSWORD` | No | Default in .env.example |
| `LOG_LEVEL` | No | `INFO` (default), `DEBUG`, `WARNING` |

---

## Production deployment

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

The prod override removes volume bind-mounts, runs 4 Uvicorn workers, sets memory/CPU limits, and adds `restart: unless-stopped` to all services.

---

## Comparison with alternatives

| | Arkhe | InvenioRDM | Zenodo (hosted) |
|---|---|---|---|
| Self-hostable | Yes | Yes | No |
| Setup time | ~5 min | 2–8 hours | N/A (SaaS) |
| Min RAM (single node) | ~2 GB | ~16 GB | N/A |
| Services required | 9 | 30+ | N/A |
| Kubernetes required | No | Recommended | N/A |
| DOI minting (DataCite) | No | Yes | Yes |
| Record versioning | No | Yes | Yes |
| Communities / collections | No | Yes | Yes |
| Access control (embargoes, restricted) | No | Yes | Yes |
| FAIR JSON-LD metadata | Yes | Yes | Yes |
| ORCID login | Yes | Yes | Yes |
| Full-text search | Yes (OpenSearch) | Yes (Elasticsearch) | Yes |
| File size limit | 2 GB (configurable) | Configurable | 50 GB |
| Background file parsing | Yes (CSV/JSON/PDF/ROOT) | Plugin-based | No |

### Measured resource usage

Numbers from `docker stats` on a laptop (Intel i7, 12 GB RAM, WSL2), idle with no records:

| Container | Memory |
|---|---|
| backend (FastAPI + uvicorn) | 122 MiB |
| celery-worker | 91 MiB |
| celery-flower | 51 MiB |
| minio | 81 MiB |
| postgres | 59 MiB |
| redis | 7 MiB |
| **opensearch** | **~1 GiB** |
| **Total** | **~1.4 GiB** |

OpenSearch accounts for most of the footprint. If you replace it with PostgreSQL full-text search (a future option), the whole stack would fit in ~450 MiB.

Search latency (p50 / p95, measured inside the container, 200 requests at concurrency 10):

- `GET /api/records` — 11 ms / 22 ms
- `GET /api/search?q=` — 12 ms / 58 ms

---

## Honest scope

A pre-built Docker image is available on Docker Hub — no build step needed:

```bash
docker pull karandev7/arkhe-backend:latest
docker pull karandev7/arkhe-frontend:latest
```

See the [Quick start](#quick-start) section for the full setup using the pre-built images.

**Arkhe works well if you:**

- Want your own private repository that stays on your servers
- Are at an institution where data can't go to external services
- Are running a course, workshop, or summer school and need somewhere for participants to upload work
- Need something running quickly without a complex setup
- Work in an offline or restricted network environment

**Arkhe is not the right tool if you:**

- Want a **public, permanently archived record with a DOI** — just use [Zenodo](https://zenodo.org) directly, it's free and built for that
- Need **record versioning, embargo controls, or community curation** — InvenioRDM handles all of that and is the right choice for a serious institutional repository
- Expect to grow to **tens of thousands of records** — Arkhe's OpenSearch and PostgreSQL setup is intentionally minimal and hasn't been tuned for large scale

I built this to fill a specific gap, not to compete with Zenodo or InvenioRDM. If either of those fits your situation, use them.

---

## References

- Wilkinson, M. D. et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data*, 3, 160018. https://doi.org/10.1038/sdata.2016.18
- InvenioRDM documentation — https://inveniordm.docs.cern.ch
- InvenioRDM system requirements — https://inveniordm.docs.cern.ch/install/requirements/
- Zenodo — https://zenodo.org
- ORCID Public API — https://info.orcid.org/documentation/features/public-api/
- OpenSearch documentation — https://opensearch.org/docs/latest/
- MinIO documentation — https://min.io/docs/minio/linux/index.html
- HEP Software Foundation — https://hepsoftwarefoundation.org
- schema.org Dataset — https://schema.org/Dataset

---

## License

MIT — see [LICENSE](LICENSE).
