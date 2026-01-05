#!/bin/bash

# Script to set up editable install and run pytest

# Exit on error
set -e

echo "Installing package in editable mode with dev dependencies..."
pip install -e ".[dev]"

echo "Running tests..."
pytest -v

echo "Project setup completed successfully"