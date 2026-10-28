.PHONY: up down test test-backend test-frontend e2e lint audit ingest format build

up:
	docker compose up --build

down:
	docker compose down -v

test: test-backend test-frontend

test-backend:
	cd backend && python -m pytest -q

test-frontend:
	cd frontend && npm run test --if-present

e2e:
	cd frontend && npx playwright test --if-present

lint:
	cd backend && ruff check . && mypy .
	cd frontend && npm run lint --if-present && npx tsc --noEmit --if-present

audit:
	cd backend && pip-audit --if-present || true
	cd frontend && npm audit --audit-level=high --if-present || true

ingest:
	cd backend && python -m app.ingestion.cli

format:
	cd backend && ruff format . --if-present
	cd frontend && npm run format --if-present
