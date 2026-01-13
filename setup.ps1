# Script to set up editable install and run pytest in PowerShell

# Exit on any error
$ErrorActionPreference = "Stop"

Write-Host "Installing package in editable mode with dev dependencies..."
pip install -e ".[dev, notebook]"

Write-Host "Running tests..."
pytest -v

Write-Host "Project setup completed successfully"