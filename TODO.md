# TODO

This file tracks planned tasks, improvements and features for `templisafe`.
Do **not** include completed work - that goes in [`CHANGELOG.md`](CHANGELOG.md).

---

## High Priority
- [ ] Develop architectural, consumer and developer documentations
- [ ] Release the library on pip
- [ ] Add a test for Templater concurrency
- [ ] Develop LLM templating use case
- [ ] Develop email template use case
- [ ] Document pydantic fields (In particular of Settings)

## Medium Priority
- [ ] Add TestPyPI staging publishing before production PyPI releases
- [ ] Add CI coverage reporting
- [ ] Refactor TemplateEngineSettings config parameter, which actually can be also a json or yaml string
- [ ] Improve error messages
- [ ] Implement async sources and SourceExecutorLine concept (dividing sources in three lines)  
- [ ] Implement a min heap for the HttpSession Management

## Low Priority
- [ ] Add schema inference during the rendering when no schema is specified
- [ ] Add support for GCP (GCPSource)
- [ ] Add support for Azure (AzureSource)
