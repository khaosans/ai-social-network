.PHONY: install test lint format clean run-backend run-frontend run-agent run-all stop-all

# Installation
install:
	poetry install
	poetry run pre-commit install

# Development
run-backend:
	cd backend && poetry run ./start.sh

run-frontend:
	cd frontend && poetry run ./start.sh

run-agent:
	cd agent && poetry run ./start.sh

run-all:
	make run-backend & make run-frontend & make run-agent

stop-all:
	pkill -f "uvicorn|python.*main:app" && lsof -ti :8080 | xargs kill -9 2>/dev/null || true

# Testing
test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=app --cov-report=html

# Code Quality
format:
	poetry run black .
	poetry run isort .

lint:
	poetry run ruff check .
	poetry run mypy .

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name ".DS_Store" -delete

# Help
help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies and set up pre-commit hooks"
	@echo "  make run-backend  Start the backend server"
	@echo "  make run-frontend Start the frontend server"
	@echo "  make run-agent    Start the agent service"
	@echo "  make run-all     Start all services"
	@echo "  make stop-all    Stop all running services"
	@echo "  make test        Run tests"
	@echo "  make test-cov    Run tests with coverage report"
	@echo "  make format      Format code with black and isort"
	@echo "  make lint        Run linting checks"
	@echo "  make clean       Clean up cache and temporary files" 