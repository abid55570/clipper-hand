.PHONY: help dev up down build test lint migrate seed clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start all services in development mode
	docker compose up --build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build all containers
	docker compose build

test: ## Run all tests
	docker compose exec backend pytest tests/ -v

test-unit: ## Run unit tests only
	docker compose exec backend pytest tests/unit/ -v

test-integration: ## Run integration tests
	docker compose exec backend pytest tests/integration/ -v

migrate: ## Run database migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

seed: ## Seed the database with sample data
	docker compose exec backend python -m scripts.seed_db

clean: ## Remove all containers, volumes, and uploads
	docker compose down -v
	rm -rf uploads/ media/

logs: ## Tail logs for all services
	docker compose logs -f

logs-worker: ## Tail worker logs
	docker compose logs -f worker

shell-backend: ## Open a shell in the backend container
	docker compose exec backend bash

shell-worker: ## Open a shell in the worker container
	docker compose exec worker bash
