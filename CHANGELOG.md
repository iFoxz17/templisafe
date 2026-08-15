# Changelog

## Unreleased

### Added

- Restored the public `TemplaterFactory().create()` workflow.
- Added public API tests for compile, render, validate and build.
- Added broader public API integration tests and a test README.
- Added regression coverage for explicit `default: null` schema fields.
- Added CI quality gates with Ruff and mypy.
- Added GitHub Actions quality and test CI for `main` and `develop`, including Python 3.14.
- Added release workflow for the `release` branch.
- Added package build validation and PyPI trusted publishing.
- Added pre-commit hooks for Ruff and mypy checks.

### Changed

- Rewired `Templater` to use the current source executor request/result model.
- Updated service helpers and tests to work with Pydantic `TaskBundle` models.
- Made HTTP async stress tests suitable for regular CI.
- Moved setup scripts into `contributing/` and grouped pytest files under `test/`.
- Moved internal root modules under `templisafe.core`.
- Consolidated formatting and linting configuration around Ruff with a 120-character line length.
- Fixed existing source mypy complaints without suppressing mypy error codes.
- Updated README, contributing, CI and test documentation for the operative workflow.

### Fixed

- Fixed schema parsing so explicit null defaults are not treated as required fields.
- Fixed schema and variant loaders to initialize managers with default manager settings.
- Restored compatibility for the old HTTP session settings import path.
