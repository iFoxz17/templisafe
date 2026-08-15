# Contributing

Thanks for helping improve `templisafe`.

## Local Setup

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate it.

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Bash:

```bash
source .venv/bin/activate
```

3. Install the package with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

4. Run the test suite:

```bash
python -m pytest -c test/pytest.ini
```

5. Run the same quality checks used by CI:

```bash
python -m ruff check src test
python -m ruff format --check src test
python -m mypy src
```

6. Install the pre-commit hook:

```bash
python -m pre_commit install
```

The helper scripts `contributing/setup.ps1` and `contributing/setup.sh` perform
the editable install and run pytest, but the explicit commands above are the
canonical workflow.

Tests and pytest configuration live under `test/`. The executable test suites
are in `test/test/`.

## Branches And CI

- Use `develop` for integration work.
- Use `main` for stable releases.
- Pull requests into `develop` or `main` run GitHub Actions quality checks and
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
