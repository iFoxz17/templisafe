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
python -m pytest test -q
```

The helper scripts `setup.ps1` and `setup.sh` perform the editable install and
run pytest, but the explicit commands above are the canonical workflow.

## Branches And CI

- Use `develop` for integration work.
- Use `main` for stable releases.
- Pull requests into `develop` or `main` run GitHub Actions.
- The current CI scope is intentionally small: install the package and run tests.
  Code quality checks and release automation will be added later.

## Pull Request Expectations

- Keep changes focused.
- Add or update tests for user-visible behavior and bug fixes.
- Update `README.md`, `doc/README.md`, `CHANGELOG.md` or `TODO.md` when behavior,
  workflow or project status changes.
- Do not include completed work in `TODO.md`; record completed user-facing changes
  in `CHANGELOG.md`.
