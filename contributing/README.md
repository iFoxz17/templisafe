# Contributing

Thanks for helping improve `templisafe`.

This guide describes the local workflow used by maintainers and contributors.
The project currently supports Python `>=3.11`.

## Local Setup

Create and activate a virtual environment from the repository root:

```bash
python -m venv .venv
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Bash:

```bash
source .venv/bin/activate
```

Install the package with development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Install pre-commit hooks:

```bash
python -m pre_commit install
```

The helper scripts `contributing/setup.ps1` and `contributing/setup.sh` perform
the full contributor setup after the virtual environment has been activated.
They install development and notebook dependencies, install pre-commit hooks,
run quality checks, and run tests with coverage.

## Quality Checks

Ruff is used for linting, import sorting and formatting checks. Mypy is used for
static type checking.

Run the same quality checks used by CI:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src
```

## Tests

Pytest configuration lives in `test/pytest.ini`. The executable test suites live
under `test/test/`.

Run the full test suite:

```bash
python -m pytest -c test/pytest.ini
```

Run tests with coverage:

```bash
python -m pytest -c test/pytest.ini -q --cov=templisafe --cov-report=term-missing --cov-report=xml:coverage.xml
```

The current minimum coverage threshold is `80%`.

Useful subsets:

```bash
python -m pytest -c test/pytest.ini -m unit
python -m pytest -c test/pytest.ini -m integration
python -m pytest -c test/pytest.ini -m stress
python -m pytest -c test/pytest.ini -m "source and http"
```

Run a file or a single test:

```bash
python -m pytest -c test/pytest.ini test/test/integration/test_templater_basic_workflows.py
python -m pytest -c test/pytest.ini test/test/integration/test_templater_basic_workflows.py::test_compile_render_validate_and_build_with_inline_sources
```

## Branches And CI

- Use `dev` for integration work.
- Use `main` for stable releases.
- Use `release` for release publication.
- Pull requests into `dev` or `main` run GitHub Actions quality checks and
  tests.
- Pushes to the `release` branch run the release pipeline: quality checks,
  tests, package build, tag and GitHub release creation, then PyPI publishing.
- PyPI publishing uses trusted publishing. Configure a PyPI trusted publisher
  for this repository and the `pypi` GitHub environment before the first
  release.

## Pull Request Expectations

- Keep changes focused.
- Add or update tests for user-visible behavior and bug fixes.
- Update `README.md`, `doc/README.md`, `CHANGELOG.md` or `TODO.md` when behavior,
  workflow or project status changes.
- Do not include completed work in `TODO.md`; record completed user-facing changes
  in `CHANGELOG.md`.
- Run Ruff, mypy and pytest before opening the pull request.
- Make sure coverage remains above the configured threshold.
