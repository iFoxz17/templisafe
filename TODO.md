# TODO

This file tracks planned tasks, improvements and features for `templisafe`.
Do **not** include completed work - that goes in [`CHANGELOG.md`](CHANGELOG.md).

---

## High Priority
- [ ] Implement async sources and SourceExecutorLine concept (dividing sources in three lines)  
- [ ] Add support for HOCON configuration language
- [ ] Add support for INI configuration language
- [ ] Add support for .env configuration language
- [ ] Implement EnvSource
- [ ] Setup github repo: automate release pipeline to create tags on release branch
- [ ] Add a test for Templater concurrency
- [ ] Develop contribuiting section
- [ ] Develop IaC use case
- [ ] Develop email use case to show concurrency in handling thousands of sources
- [ ] Release the library on pip
- [ ] Document pydantic fields (In particular of Settings)

## Medium Priority
- [ ] Refactor TemplateEngineSettings config parameter, which actually can be also a json or yaml string
- [ ] Improve error messages
- [ ] Implement a min heap for the HttpSession Management
- [ ] Advertise library on r/python
- [ ] Advertise library on hackernews
- [ ] Advertise library on medium

## Low Priority
- [ ] Add schema inference during the rendering when no schema is specified
- [ ] Add support for GCP (GCPSource)
- [ ] Add support for Azure (AzureSource)