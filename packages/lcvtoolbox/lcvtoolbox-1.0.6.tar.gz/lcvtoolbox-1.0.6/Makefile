.PHONY: help install install-dev test lint format check build clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

create_venv:  ## Create a virtual environment
	python3 -m venv venv
	@echo "Virtual environment created in 'venv/'"
	@echo "Activate it with 'source venv/bin/activate' (Linux/Mac) or 'venv\\Scripts\\activate' (Windows)"

activate_venv:  ## Activate the virtual environment
	@echo "To activate the virtual environment, run:"
	@echo "source venv/bin/activate"  # Linux/Mac
	@echo "venv\\Scripts\\activate"  # Windows

activate:  ## Show how to activate the virtual environment
	@echo "To activate the virtual environment, run one of these commands in your shell:"
	@echo ""
	@echo "For Linux/Mac:"
	@echo "  source venv/bin/activate"
	@echo ""
	@echo "For Windows:"
	@echo "  venv\\Scripts\\activate"
	@echo ""
	@echo "Note: This must be run directly in your shell, not through Make"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=cv_toolbox --cov-report=html --cov-report=xml

lint:  ## Run linting checks
	ruff check cv_toolbox/ tests/
	mypy cv_toolbox/

format:  ## Format code and fix auto-fixable issues
	ruff check --fix cv_toolbox/ tests/
	ruff format cv_toolbox/ tests/

check:  ## Run all checks (linting, formatting, type checking)
	ruff check cv_toolbox/ tests/
	ruff format --check cv_toolbox/ tests/
	mypy cv_toolbox/

build:  ## Build package
	python -m build

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development workflow
dev-setup: install-dev  ## Set up development environment
	@echo "Development environment ready!"
	@echo "Run 'make format' to format code"
	@echo "Run 'make check' to run all checks"
	@echo "Run 'make test' to run tests"

# CI simulation
ci: check test  ## Run CI checks locally
