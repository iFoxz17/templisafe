# Changelog

## Unreleased

### Added

- Restored the public `TemplaterFactory().create()` workflow.
- Added GitHub Actions test CI for `main` and `develop`.
- Added public API tests for compile, render, validate and build.
- Added regression coverage for explicit `default: null` schema fields.

### Changed

- Rewired `Templater` to use the current source executor request/result model.
- Updated service helpers and tests to work with Pydantic `TaskBundle` models.
- Made HTTP async stress tests suitable for regular CI.
- Updated README and contributing documentation for the first operative version.

### Fixed

- Fixed schema parsing so explicit null defaults are not treated as required fields.
- Fixed schema and variant loaders to initialize managers with default manager settings.
- Restored compatibility for the old HTTP session settings import path.
