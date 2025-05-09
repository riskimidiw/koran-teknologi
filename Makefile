.PHONY: help install test check format clean run run-http

# Colors for pretty output
GREEN := \033[0;32m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

# Python and Poetry settings
PYTHON := python3
POETRY := poetry
DAYS := 1
DRY_RUN :=
HTTP_HOST := 0.0.0.0
HTTP_PORT := 8000

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install project dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@$(POETRY) install
	@$(POETRY) run pip install -e .
	@$(POETRY) run pip install types-requests

lint: ## Run code quality checks
	@echo "$(GREEN)Running code quality checks...$(NC)"
	# Black: Formats code to a consistent style, no decisions needed
	@$(POETRY) run black --check --exclude ".venv/" .
	# isort: Specifically handles import sorting and organization
	@$(POETRY) run isort --check-only --skip .venv .
	# flake8: Checks for PEP 8 style guide, complexity, and common errors
	@$(POETRY) run flake8 --ignore=E501 --exclude=.venv .

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	@$(POETRY) run black .
	@$(POETRY) run isort .

setup: ## Initial project setup
	@echo "$(GREEN)Setting up project...$(NC)" || (echo "$(RED)Poetry is not installed. Please install it first: https://python-poetry.org/docs/#installation$(NC)" && exit 1)
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "⚠️  Please update .env with your Telegram credentials"; \
	fi
	@mkdir -p logs
	@$(MAKE) install

run: ## Run the blog checker (use DAYS=n for custom days, DRY_RUN for dry run)
	@echo "$(GREEN)Running blog checker...$(NC)"
	@$(POETRY) run python main.py cli $(if $(DRY_RUN),--dry-run) --days $(DAYS)

run-http: ## Run the HTTP server (use HTTP_HOST and HTTP_PORT for custom host/port)
	@echo "$(GREEN)Starting HTTP server on $(HTTP_HOST):$(HTTP_PORT)...$(NC)"
	@$(POETRY) run python main.py http --host $(HTTP_HOST) --port $(HTTP_PORT)

clean: ## Remove temporary files and build artifacts
	@echo "$(GREEN)Cleaning project...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "*.egg" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name "build" -exec rm -rf {} +
	@find . -type d -name "dist" -exec rm -rf {} +
	@rm -rf .coverage coverage.xml htmlcov/

.DEFAULT_GOAL := help