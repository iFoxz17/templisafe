# TODO

This file tracks planned tasks, improvements and features for `templisafe`.
Do **not** include completed work - that goes in [`CHANGELOG.md`](CHANGELOG.md).

---

## High Priority
- [ ] Save generated schema metadata (as index_key) using Annotated as done with Task
- [ ] Parse the schema and the variants using a pydantic model
- [ ] Manage Unions types in schema and variants 
- [ ] Implement async sources and SourceExecutorLine concept (dividing sources in three lines)  
- [ ] Add a test for Templater concurrency
- [ ] Develop IaC use case
- [ ] Develop email use case to show concurrency in handling thousands of sources
- [ ] Release the library on pip
- [ ] Document pydantic fields (In particular of Settings)

## Medium Priority
- [ ] Add TestPyPI staging publishing before production PyPI releases
- [ ] Add CI coverage reporting
- [ ] Refactor TemplateEngineSettings config parameter, which actually can be also a json or yaml string
- [ ] Improve error messages
- [ ] Implement a min heap for the HttpSession Management
- [ ] Add support for HOCON configuration language
- [ ] Add support for INI configuration language
- [ ] Add support for .env configuration language
- [ ] Implement EnvSource

## Low Priority
- [ ] Add schema inference during the rendering when no schema is specified
- [ ] Add support for GCP (GCPSource)
- [ ] Add support for Azure (AzureSource)
