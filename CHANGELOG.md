# Changelog

All notable changes to this project will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

## Unreleased

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.1] - 2026-08-17

### Fixed

- Fixed package imports for base installations without optional AWS dependencies.
- Lazy-load AWS source implementations and dependencies only when AWS sources are used.
- Added clearer optional dependency errors for AWS and async HTTP source features.

## [0.1.0] - 2026-08-17

### Added

- Initial public release of `templisafe`.
- Added Template-as-Code workflows through `compile`, `validate`, `render` and `build`.
- Added Pydantic-backed schema validation for template variables.
- Added support for inline, local, HTTP and AWS source settings.
- Added Jinja template engine support, Django engine support and custom engine extension points.
- Added YAML, JSON, TOML and XML configuration parsing for schemas, variants and settings.
- Added configurable settings for sources, parsers, engines, executors, compiler and renderer.
- Added integration, unit and stress test coverage with CI quality gates.

## Release Template

```markdown
## [x.y.z] - yyyy-mm-dd

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security
```
