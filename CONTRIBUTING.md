# Contributing to Arkhe

Thank you for your interest in contributing! This document describes how to get started, our coding conventions, and the pull request process.

## Getting started

1. Fork the repository and clone your fork.
2. Copy `.env.example` to `.env` and fill in the required values (see README).
3. Start the development stack:

   ```bash
   docker compose up postgres redis minio opensearch
   ```

4. Install backend dependencies and run tests:

   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   pytest -x -q
   ```

5. Install frontend dependencies:

   ```bash
   cd frontend && npm install && npm run dev
   ```

## Code style

- **Python**: formatted with [ruff](https://docs.astral.sh/ruff/). Run `ruff check app/` before opening a PR.
- **TypeScript**: the project uses strict TypeScript. Run `npx tsc --noEmit` to confirm no type errors.
- **Commits**: use the imperative mood and a short scope prefix, e.g. `backend: fix presigned URL expiry`, `frontend: add keyword filter chip`.

## Pull requests

- Keep PRs focused — one logical change per PR.
- All new backend endpoints should have at least one test in `backend/tests/`.
- CI must pass before a PR can be merged (backend pytest + ruff, frontend tsc + build).
- Reference any related issue in the PR description.

## Reporting bugs

Please open a GitHub issue with:
- a short description of the problem
- steps to reproduce
- expected vs. actual behaviour
- your OS and Docker version

## License

By contributing you agree that your changes will be released under the [MIT License](LICENSE).
