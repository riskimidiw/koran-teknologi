.PHONY: help install test check format clean run

# Colors for pretty output
GREEN := \033[0;32m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Python and Poetry settings
PYTHON := python3
POETRY := poetry
DAYS := 1
DRY_RUN :=

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install project dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@$(POETRY) install
	@$(POETRY) run pip install -e .

check: ## Run code quality checks
	@echo "$(GREEN)Running code quality checks...$(NC)"
	@$(POETRY) run black --check .
	@$(POETRY) run isort --check-only .
	@$(POETRY) run flake8 .
	@$(POETRY) run mypy .

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	@$(POETRY) run black .
	@$(POETRY) run isort .

setup: ## Initial project setup
	@echo "$(GREEN)Setting up project...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "⚠️  Please update .env with your Telegram credentials"; \
	fi
	@mkdir -p logs
	@$(MAKE) install

run: ## Run the blog checker (use DAYS=n for custom days, DRY_RUN=1 for dry run)
	@echo "$(GREEN)Running blog checker...$(NC)"
	@$(POETRY) run python main.py $(if $(DRY_RUN),--dry-run) --days $(DAYS)

.DEFAULT_GOAL := help