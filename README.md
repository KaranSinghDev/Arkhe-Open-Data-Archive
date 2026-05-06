# Arkhe

*From the Greek ἀρχή — origin, beginning, source.*

A self-hostable, lightweight scientific data repository built for research groups, university departments, and teaching environments that need FAIR-compliant data sharing without the operational overhead of a full-scale platform.

---

## Background

[Zenodo](https://zenodo.org) is a general-purpose research data repository operated by CERN. It is widely used across disciplines and genuinely solves the problem of making research outputs publicly citable. [InvenioRDM](https://inveniosoftware.org/products/rdm/) is the open-source framework that powers Zenodo, and it is a serious, production-grade system.

Working with and reading about these platforms surfaced a recurring pattern: the software behind them is not straightforward to self-host. InvenioRDM's own documentation acknowledges it requires Kubernetes or a multi-service Docker setup, a minimum of ~16 GB RAM, familiarity with Elasticsearch/OpenSearch cluster management, and a non-trivial amount of configuration before the first record can be uploaded. Threads in the HEP Software Foundation community, InvenioRDM's GitHub issues, and discussions on ResearchSoftwareEngineering forums reflect a consistent need: something that behaves like Zenodo for a research group's internal use, but which a single person can stand up on a lab VM in an afternoon.

The specific situations that came up repeatedly:

- A department wanting its own repository for student theses and coursework data, without sending pre-publication work to a public external service
- Research groups at institutions with data-residency or compliance requirements that prevent uploading to CERN-operated infrastructure
- Workshop and summer school organizers who need participants to share datasets and analysis code for the duration of an event
- Labs operating in air-gapped or restricted network environments

Arkhe is an attempt to address this gap: a system that implements the same core concepts (ORCID login, file upload, full-text search, FAIR metadata) with a setup time measured in minutes rather than days.

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
curl -O https://raw.githubusercontent.com/your-org/arkhe/main/docker-compose.hub.yml
curl -O https://raw.githubusercontent.com/your-org/arkhe/main/.env.example
cp .env.example .env
# Edit .env — set ORCID_CLIENT_ID, ORCID_CLIENT_SECRET, SECRET_KEY,
#             POSTGRES_PASSWORD, MINIO_ROOT_PASSWORD, ORCID_REDIRECT_URI
docker compose -f docker-compose.hub.yml up -d
```

### Option B — build from source

```bash
git clone https://github.com/your-org/arkhe.git
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
| Min RAM (single node) | ~4 GB | ~16 GB | N/A |
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

---

## Honest scope

**Arkhe is a good fit for:**

- A research group or department that wants an internal repository without sending data to an external service
- Institutions with data-residency requirements
- Teaching environments where students upload datasets and analysis outputs
- Small collaborations (up to a few thousand records) that need something running quickly
- Air-gapped or restricted-network deployments

**Arkhe is not a replacement for:**

- **Zenodo itself** — if you want a public, globally indexed, DOI-minted, permanently archived record, upload to Zenodo. That is what it is built for.
- **InvenioRDM** — if your institution needs record versioning, embargo controls, community curation, DataCite DOI minting, or expects to grow to hundreds of thousands of records, InvenioRDM is the right choice. It is a production system maintained by a dedicated team at CERN.
- **Large-scale repositories** — Arkhe has not been benchmarked or tuned beyond moderate load. The OpenSearch and PostgreSQL configurations are intentionally minimal.

The intent is not to compete with these systems. It is to cover the gap where those systems are too heavy for the use case.

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
