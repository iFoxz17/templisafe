#!/bin/bash

set -euo pipefail

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing package in editable mode with development and notebook dependencies..."
python -m pip install -e ".[dev,notebook]"

echo "Installing pre-commit hooks..."
python -m pre_commit install

echo "Running Ruff lint checks..."
python -m ruff check .

echo "Checking formatting with Ruff..."
python -m ruff format --check .

echo "Running mypy..."
python -m mypy src

echo "Running tests with coverage..."
python -m pytest -c test/pytest.ini -q --cov=templisafe --cov-report=term-missing --cov-report=xml:coverage.xml

echo "Contributor setup completed successfully."
