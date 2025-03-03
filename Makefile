PYTHON_VERSION ?= 3.10

.PHONY: install install-prod check format-check mypy unittest test publish all clean help

install: ## Install development dependencies
	poetry install --with dev

install-prod: ## Install production dependencies
	poetry install

check: ## Run ruff check
	poetry run ruff check .

format-check: ## Run ruff format check
	poetry run ruff format --check .

mypy: ## Run mypy check
	poetry run mypy .

unittest: ## Run unit tests
	poetry run python -m unittest discover tests

test: install check format-check mypy unittest ## Run all checks and tests

publish: install-prod ## Publish to PyPI (requires PYPI_API_TOKEN environment variable to be set)
	poetry config pypi-token.pypi $(PYPI_API_TOKEN)
	poetry publish --build

clean: ## Remove virtual environment
	rm -rf .venv

all: test ## Default target: run tests

help: ## Show help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}'
