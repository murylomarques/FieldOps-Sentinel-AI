SHELL := /bin/bash

.PHONY: up down logs backend frontend test lint format seed train migrate

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

seed:
	python scripts/seed_demo_data.py

train:
	python ml/scripts/generate_synthetic_data.py --rows 5000
	python ml/scripts/train_models.py

test:
	cd backend && pytest -q

lint:
	cd backend && ruff check app tests
	cd frontend && npm run lint

format:
	cd backend && ruff format app tests
	cd frontend && npm run format

migrate:
	@echo "Alembic migration scaffolding is not yet wired. See docs/assumptions.md"
