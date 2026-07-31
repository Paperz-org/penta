.DEFAULT_GOAL := help

.PHONY: help
help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install dependencies
	uv pip install -e ".[test,doc,dev]"

.PHONY: lint
lint: ## Run code linters
	ruff format --preview --check penta tests
	ruff check --preview penta tests
	mypy penta

.PHONY: fmt format
fmt format: ## Run code formatters
	ruff format --preview penta tests
	ruff check --preview --fix penta tests 

.PHONY: test
test: ## Run tests
	uv run pytest .

.PHONY: test-cov
test-cov: ## Run tests with coverage
	uv run pytest --cov=penta --cov-report term-missing tests

.PHONY: docs
docs: ## Serve documentation locally
	pip install -r docs/requirements.txt
	cd docs && mkdocs serve -a localhost:8090
