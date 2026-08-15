# Script to set up editable install and run pytest in PowerShell

# Exit on any error
$ErrorActionPreference = "Stop"

Write-Host "Installing package in editable mode with dev dependencies..."
pip install -e ".[dev, notebook]"

Write-Host "Running tests..."
python -m pytest -c test/pytest.ini -v

Write-Host "Project setup completed successfully"
