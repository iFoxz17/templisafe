# TODO

This file tracks planned tasks, improvements and features for `templisafe`.
Do **not** include completed work - that goes in [`CHANGELOG.md`](CHANGELOG.md).

---

## High Priority

- [ ] Release the library on PyPI
- [ ] Add support for user-defined Python objects in schemas and variants
- [ ] Document supported settings fields, schema types, constraints and metadata

## Medium Priority

- [ ] Add TestPyPI staging publishing before production PyPI releases
- [ ] Improve error messages
- [ ] Clarify and refactor `TemplateEngineSettings.config` input semantics
- [ ] Extend stress tests for local sources
- [ ] Extend stress tests for synchronous HTTP sources
- [ ] Add a benchmark/performance baseline for compile, validate, render and build
- [ ] Develop LLM templating use case
- [ ] Develop email template use case

## Low Priority

- [ ] Implement async sources and `SourceExecutorLine` concept
- [ ] Optimize HTTP session reuse strategy after profiling
- [ ] Add schema inference during rendering when no schema is specified
- [ ] Add support for GCP sources
- [ ] Add support for Azure sources
