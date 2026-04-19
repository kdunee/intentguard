PYTHON_VERSION ?= 3.10

.PHONY: install install-prod check format-check mypy unittest test publish all clean help

install: ## Install development dependencies
	uv sync --dev --group validation --group dataset --locked

install-prod: ## Install production dependencies
	uv sync --no-dev --locked

check: ## Run ruff check
	uv run ruff check .

format-check: ## Run ruff format check
	uv run ruff format --check .

mypy: ## Run mypy check
	uv run mypy .

unittest: ## Run unit tests
	uv run python -m unittest discover tests

test: install check format-check mypy unittest ## Run all checks and tests

publish: install-prod ## Publish to PyPI (requires UV_PUBLISH_TOKEN environment variable to be set)
	rm -rf dist
	uv build --no-sources
	uv publish

clean: ## Remove virtual environment
	rm -rf .venv

all: test ## Default target: run tests

help: ## Show help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}'
