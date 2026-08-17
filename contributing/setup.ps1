$ErrorActionPreference = "Stop"

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing package in editable mode with development and notebook dependencies..."
python -m pip install -e ".[dev,notebook]"

Write-Host "Installing pre-commit hooks..."
python -m pre_commit install

Write-Host "Running Ruff lint checks..."
python -m ruff check .

Write-Host "Checking formatting with Ruff..."
python -m ruff format --check .

Write-Host "Running mypy..."
python -m mypy src

Write-Host "Running tests with coverage..."
python -m pytest -c test/pytest.ini -q --cov=templisafe --cov-report=term-missing --cov-report=xml:coverage.xml

Write-Host "Contributor setup completed successfully."
