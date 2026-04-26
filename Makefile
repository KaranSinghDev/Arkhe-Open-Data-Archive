.PHONY: up down build migrate test lint shell logs

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose exec backend alembic upgrade head

test:
	docker compose exec backend pytest -x -q

lint:
	docker compose exec backend ruff check app/
	cd frontend && npx tsc --noEmit

shell:
	docker compose exec backend bash

logs:
	docker compose logs -f backend celery-worker

prod-up:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

prod-down:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down
