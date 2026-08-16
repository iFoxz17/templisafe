# Architecture

This document describes the intended internal architecture of `templisafe`.
It is written for maintainers and contributors. The companion
[user guide](user-guide.md) focuses on public usage.

## Architectural Goal

`templisafe` separates user-facing workflows from the mechanics required to
load, parse, validate and render templates.

At the highest level, public API methods create a validated `Task`. A
`ServiceOrchestrator` then transforms the task through a sequence of services
until it becomes a domain result:

```text
Templater API
  -> TaskBundle
  -> Task
  -> TaskValidator
  -> ServiceOrchestrator
  -> SourceService
  -> DataService
  -> ConfigService
  -> SettingsService
  -> ComponentService
  -> ResourceService
  -> OutcomeHandler
```

The public API should remain small even as source types, template engines,
parsers and execution strategies grow.

## Module Responsibilities

### `templisafe`

Public library surface. It exports the user-facing `Templater`,
`TemplaterFactory`, domain models, settings, content types and diagnostic
policy.

Only stable public entry points should live at this level.

### `templisafe.core`

Shared primitives that support multiple architectural layers:

- metadata containers used to classify task bundle fields.
- collection helpers used by immutable settings models.
- diagnostic policy and default manager settings.

This package should stay small and dependency-light. It must not know about
sources, parsers, services or template rendering.

### `templisafe.task`

Task abstractions used to move public API calls into the service pipeline:

- task models: `Task`, `TaskBundle`, `CompilationBundle`, `RenderingBundle`,
  `BuildBundle`.
- task typing: `TaskType`.
- field categorization: `FieldCategory` and `CategoryMetadata`.
- task validation: `TaskValidator`.

The task model is the bridge between the public API and the service pipeline.

### `templisafe.handler`

Boundary handlers that apply caller-facing diagnostic behavior:

- `DiagnosticHandler`: reusable diagnostic policy engine.
- `OutcomeHandler`: converts compilation/rendering outcomes into warnings,
  logs or exceptions according to `DiagnosticPolicy`.

Handlers sit at the edges of workflows. They should not perform resource
loading, parsing, compilation or rendering themselves.

### `templisafe.content`

Raw loaded data:

- `Content`: string payload plus content type.
- `ContentType`: `TEXT`, `YAML`, `JSON`, `TOML`, `XML`.

Sources produce `Content`; parsers consume it.

### `templisafe.settings`

Immutable Pydantic settings objects used to configure the library.

Important settings families:

- source settings.
- source executor settings.
- parser settings.
- template engine settings.
- compiler and renderer settings.
- manager/cache settings.

Settings are serializable by design. They are the preferred way to pass
configuration across public boundaries.

### `templisafe.source`

Source abstractions and concrete readers:

- `Source`: synchronous open/read/close lifecycle.
- `AsyncSource`: async lifecycle for async-capable implementations.
- inline and local sources.
- HTTP sources.
- AWS sources.
- source factories, managers, resolvers and assemblers.
- content type resolution.

A source should know how to read bytes/text from one location, but it should not
parse configuration or understand templates.

### `templisafe.executor`

Strategies for reading multiple sources:

- `SourceExecutor`: execution abstraction.
- `SequentialSourceExecutor`: reads sources sequentially.
- `ThreadPoolSourceExecutor`: reads sources concurrently.
- retry policy creation through Tenacity.
- source latency strategy optimization.
- executor factory, manager, resolver and assembler.

Executors preserve request ordering in their results.

### `templisafe.parser`

Conversion from raw content/configuration into structured objects:

- config parsers for YAML, JSON, TOML and XML.
- settings parsers.
- template parser.
- schema parser and type parser.
- variant parser.

Parsers should not read sources and should not render templates.

### `templisafe.engine`

Template engine adapters:

- `TemplateEngine`: extracts variables and renders strings.
- `JinjaTemplateEngine`: default implementation.
- `DjangoTemplateEngine`: alternate implementation.
- engine factory, manager, resolver and assembler.

Engines hide third-party template engine APIs from the rest of the library.

### `templisafe.template`

Domain model and domain operations:

- `template_model.py`: `Template`, `Schema`, `Compilation`,
  `VariantSet`, `Rendering`, `Build`, `Outcome`, `Diagnostic` and related
  value objects.
- `Compiler`: validates template variables against schema fields.
- `Renderer`: validates variants and renders parameterizations.
- compiler and renderer factory/manager/resolver/assembler classes.

This package should operate on already loaded domain models, not on sources or
raw configuration files.

### `templisafe.provider`

Small facades around resolvers and domain operations.

Provider families:

- source providers: source and content provision.
- component providers: parsers, template engines, compiler and renderer.
- resource providers: config, settings, template, schema, variants,
  compilation and rendering.

Providers make service classes explicit and testable. A provider usually wraps
one specialized dependency and exposes a narrow `provide(...)` method.

### `templisafe.service`

Task pipeline stages.

Each service receives a task bundle and returns a copied bundle with one kind of
transformation applied:

- `SourceService`: resolves source settings to sources.
- `DataService`: opens/reads sources and returns content.
- `ConfigService`: parses structured content into config objects.
- `SettingsService`: parses settings configuration into settings objects.
- `ComponentService`: resolves configured components.
- `ResourceService`: builds domain resources and executes compilation,
  validation or rendering.
- `ServiceOrchestrator`: applies the service sequence for the task type.
- `ServiceAssembler`: wires the default service graph.

Services should not own low-level creation rules; they delegate to providers.

## Task Flow

The public API creates task bundles:

- `compile(...)` creates a `CompilationBundle`.
- `render(...)` creates a `RenderingBundle`.
- `validate(...)` creates a rendering bundle marked for validation only.
- `build(...)` creates a `BuildBundle`.

The bundle is wrapped in a `Task` and passed through `TaskValidator`.
Validation should ensure that:

- the task type matches the bundle type.
- required fields for the task type are present.
- unsupported raw input shapes are rejected early.
- rendering tasks receive a `CompilationSpec`.
- build tasks contain both template and variants.

After validation, `ServiceOrchestrator` executes the required pipeline. The
service pipeline gradually replaces user input with resolved internal objects:

```text
SourceSettings | Source | raw config
  -> Source
  -> Content
  -> Config
  -> Settings / domain model
  -> Compilation / Rendering / Build
```

## Compile Flow

```text
CompilationBundle
  -> SourceService
  -> DataService
  -> ConfigService
  -> SettingsService
  -> ComponentService
  -> ResourceService
  -> Compilation
```

`ResourceService` creates a `Template`, optionally creates a `Schema`, resolves
a `Compiler`, and returns `Compilation`.

## Render Flow

```text
RenderingBundle
  -> SourceService
  -> DataService
  -> ConfigService
  -> SettingsService
  -> ComponentService
  -> ResourceService
  -> Rendering
```

`ResourceService` creates a `VariantSet`, resolves a `Renderer`, resolves a
template engine only for rendering, and returns `Rendering`.

Validation follows the same flow but calls renderer validation instead of full
rendering.

## Build Flow

```text
BuildBundle
  -> compile subtask
  -> render subtask
  -> Build
```

Build should reuse the same orchestrated machinery as compile and render rather
than duplicating their implementation.

## Core Abstraction Pattern

Many packages use the same construction pattern:

- `Settings`: immutable configuration.
- `Factory`: creates concrete implementations from settings.
- `Manager`: optional cache around a factory.
- `Resolver`: accepts an existing object, settings object or default.
- `Assembler`: wires a default resolver graph.
- `Provider`: task/service-facing facade around a resolver or operation.
- `Service`: transforms a task bundle using providers.

This pattern is intentionally explicit. It makes extension points visible and
keeps user-facing orchestration separate from implementation selection.

## Extension Points

### Add a source

1. Create a `SourceSettings` subclass.
2. Register its `SourceKind`.
3. Implement a `Source` subclass.
4. Add it to `SourceFactory`.
5. Add tests for content type resolution, lifecycle and executor behavior.

### Add a template engine

1. Add a `TemplateEngineKind`.
2. Implement `TemplateEngine`.
3. Register it in `TemplateEngineFactory`.
4. Add extraction and rendering tests.

### Add a config format

1. Add a `ContentType`.
2. Implement `ConfigParser`.
3. Register it in `ConfigParserFactory`.
4. Add parser and source integration tests.

### Add a parser setting

1. Extend the corresponding settings model.
2. Update the parser default.
3. Add tests for default behavior and override behavior.

## Architectural Invariants

- Public API methods should construct tasks, not perform low-level work.
- Services should transform bundles and delegate specialized work to providers.
- Providers should stay thin and deterministic.
- Sources should only read content.
- Parsers should only parse content/configuration.
- Compiler and renderer should only operate on domain models.
- Outcome handling should happen at the API boundary after task execution.
- Domain models should remain independent from IO concerns.

## Diagram Alignment

The [architecture diagram](architecture.svg) is the visual reference for this
document. The code should be kept aligned with the diagram before the first
release. When the diagram and this document diverge, update both in the same
change.
