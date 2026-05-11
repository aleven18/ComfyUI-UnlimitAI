.PHONY: help install install-dev test test-cov lint format clean build publish

# Variables
PYTHON = python3
PIP = pip3
PROJECT_NAME = ComfyUI-UnlimitAI

# Default target
help:
	@echo "$(PROJECT_NAME) - Makefile Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help          Show this help message"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  test          Run all tests"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  lint          Run all linting tools"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run type checking with mypy"
	@echo "  clean         Clean up generated files"
	@echo "  build         Build distribution packages"
	@echo "  publish       Publish to PyPI (requires credentials)"
	@echo "  check-all     Run all checks (lint, test, type-check)"
	@echo "  setup-hooks   Setup pre-commit hooks"
	@echo ""

# Installation
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	$(PYTHON) run_tests.py

test-cov:
	$(PYTHON) -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

test-fast:
	$(PYTHON) -m pytest tests/ -x -v

# Linting
lint:
	@echo "Running flake8..."
	$(PYTHON) -m flake8 nodes/ utils/ tests/ --max-line-length=100 --ignore=E203,W503
	@echo "Running bandit..."
	$(PYTHON) -m bandit -r nodes/ utils/ -ll
	@echo "Linting complete!"

# Formatting
format:
	@echo "Formatting code with black..."
	$(PYTHON) -m black . --line-length=100
	@echo "Sorting imports with isort..."
	$(PYTHON) -m isort . --profile=black --line-length=100
	@echo "Formatting complete!"

format-check:
	$(PYTHON) -m black --check . --line-length=100
	$(PYTHON) -m isort --check . --profile=black --line-length=100

# Type checking
type-check:
	@echo "Running mypy type checker..."
	$(PYTHON) -m mypy nodes/ utils/ --ignore-missing-imports
	@echo "Type checking complete!"

# All checks
check-all: lint format-check type-check test
	@echo "All checks passed!"

# Cleanup
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

# Build and publish
build: clean
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build

publish: build
	$(PYTHON) -m pip install --upgrade twine
	$(PYTHON) -m twine upload dist/*

# Pre-commit
setup-hooks:
	$(PIP) install pre-commit
	pre-commit install
	@echo "Pre-commit hooks installed!"

run-hooks:
	pre-commit run --all-files

# Development
dev-setup: install-dev setup-hooks
	@echo "Development environment setup complete!"

# Documentation
docs:
	@echo "Building documentation..."
	cd docs && $(PYTHON) -m sphinx -b html source _build/html
	@echo "Documentation built in docs/_build/html/"

# Quick start
quick-start:
	@echo "Quick start guide..."
	@echo "1. Install dependencies: make install"
	@echo "2. Configure API key: cp .env.example .env"
	@echo "3. Run tests: make test"
	@echo "4. Start developing!"
