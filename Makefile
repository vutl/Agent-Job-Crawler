.PHONY: up down status test test-fixtures clean help

help:
	@echo "AI Job Intelligence Platform Commands:"
	@echo "  make up            - Start PostgreSQL and Redis via Docker Compose"
	@echo "  make down          - Stop local Docker services"
	@echo "  make status        - Check running Docker containers"
	@echo "  make test          - Run pytest across the monorepo"
	@echo "  make test-fixtures - Run fixture tests for crawlers & schema"

up:
	docker compose up -d

down:
	docker compose down

status:
	docker compose ps

test:
	PYTHONPATH=. .venv/bin/pytest tests/

test-fixtures:
	PYTHONPATH=. .venv/bin/pytest tests/fixtures/
