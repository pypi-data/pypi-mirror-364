.PHONY: test coverage lint format clean install dev-install badge

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
coverage:
	pytest tests/ --cov=rbadata --cov-report=term-missing --cov-report=html

# Update coverage badge
badge:
	python scripts/generate_coverage_badge.py --update-readme

# Run linting
lint:
	flake8 rbadata/ --max-line-length=88 --extend-ignore=E203,W503
	black --check rbadata/
	isort --check-only rbadata/

# Format code
format:
	black rbadata/
	isort rbadata/

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

# Install package
install:
	pip install -e .

# Install with dev dependencies
dev-install:
	pip install -e ".[dev]"

# Run all checks
check: lint test coverage

# Build package
build: clean
	python -m build

# Upload to PyPI (test)
upload-test:
	python -m twine upload --repository testpypi dist/*

# Upload to PyPI
upload:
	python -m twine upload dist/*