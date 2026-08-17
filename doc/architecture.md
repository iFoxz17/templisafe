# Architecture

This document describes the internal architecture of `templisafe`. It is written
for maintainers and contributors. The companion [user guide](user-guide.md)
focuses on public usage.

The visual companion for this document is [architecture.svg](architecture.svg).
When the diagram, code and this document diverge, update them together.

## Architectural Goal

`templisafe` separates the user-facing templating workflow from the mechanics
required to load, parse, validate and render resources.

The architecture deliberately follows strictly the **single responsibility principle**.
This makes the design slightly more explicit and formal than a minimal
implementation would be, but it gives each component a clear role, keeps
responsibilities easy to reason about and makes the library easier to extend.

At the highest level, public API methods create a validated task. The task then
flows through a deterministic service pipeline until it becomes a domain result:

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

## Layers

### Public API

`Templater` is the user-facing workflow boundary. It exposes `compile`,
`validate`, `render` and `build`, converts method arguments into task bundles,
validates them, delegates execution to the service pipeline, and applies the
configured outcome policy.

`TemplaterFactory` builds a ready-to-use `Templater` by assembling default
services, providers, parsers, engines, compilers, renderers, source executors
and diagnostic handling.

Only stable public entry points should live at the top-level `templisafe`
package.

### Input

Public input models live in `templisafe.input`:

- `TemplateInput`
- `SchemaInput`
- `VariableInput`
- `VariantInput`
- `VariantSetInput`

They let users provide dynamic in-memory definitions without exposing internal
domain objects such as Pydantic-generated schema classes or `Binding` objects.
These models mirror the canonical configuration document shapes where useful.

### Task

Task abstractions live in `templisafe.task`.

`Task`, `TaskBundle`, `CompilationBundle`, `RenderingBundle` and `BuildBundle`
are the internal representation of requested work. They preserve user intent
while classifying fields as resources or components, allowing services to
transform only the relevant parts of the bundle.

`TaskValidator` validates task shape before execution:

- compile tasks need a template.
- render and validate tasks need a `CompilationSpec` and variants.
- build tasks need a template and variants.

The task layer is the bridge between the public API and the service pipeline.

### Service Pipeline

The service pipeline lives in `templisafe.service`.

`ServiceOrchestrator` owns workflow sequencing. It runs single tasks through
the service chain and implements `build` as compile plus render. If compilation
fails, build returns a failed `Build` and skips rendering; the public outcome
handler then decides whether to raise or return diagnostics.

The service stages are:

- `SourceService`: resolves `SourceSettings` into concrete `Source` objects.
- `DataService`: executes sources and replaces them with `Content`.
- `ConfigService`: parses structured content into configuration dictionaries.
- `SettingsService`: turns configuration dictionaries for component fields into
  typed `Settings`.
- `ComponentService`: resolves settings into executable components.
- `ResourceService`: turns resolved resources and components into domain
  objects and executes compile, validate or render.

Services transform task bundles. They should not own low-level creation rules;
they delegate to providers.

### Provider

Providers live in `templisafe.provider`.

Providers are thin facades around creation, parsing and domain operations. They
keep services small and explicit. A provider usually exposes one `provide(...)`
method and delegates to a resolver, parser, compiler, renderer or source
executor.

`ResourceProvider` is the aggregate facade for creating configs, settings,
templates, schemas, variant sets, compilations, validations and renderings.

`ComponentProvider` is the aggregate facade for resolving template engines,
parsers, compiler and renderer.

### Source

Sources live in `templisafe.source`.

Sources know how to read content from a location. They should not parse,
validate or render anything.

Current source families:

- inline source: content embedded in settings.
- local source: content read from the filesystem.
- HTTP source: content read from HTTP endpoints.
- AWS sources: cloud-backed sources.
- custom sources: user-provided implementations.

Async HTTP internals are optional and loaded lazily.

### Content

Content objects live in `templisafe.content`.

`Content` is the boundary object between reading and parsing. It contains a
string payload plus a `ContentType`. `ContentType` tells later stages whether the
payload is raw text or structured configuration such as YAML, JSON, TOML or XML.

### Executor

Source executors live in `templisafe.executor`.

Source executors define how multiple sources are read. The executor layer
chooses sequential or thread-pool execution, applies retry policy, and preserves
result ordering. It is about reading strategy, not parsing or template logic.

### Parser

Parsers live in `templisafe.parser`.

Parsers convert raw configuration or text into structured internal objects:

- `ConfigParser`: YAML, JSON, TOML or XML text to configuration dictionaries.
- `SettingsParser`: configuration dictionaries to settings objects.
- `TemplateParser`: template string plus extracted variables to `Template`.
- `SchemaParser`: schema configuration to a dynamic Pydantic-backed `Schema`.
- `VariantParser`: variant configuration to `VariantSet`.

Parsers should not read sources and should not render templates.

### Settings

Settings live in `templisafe.settings`.

Settings are immutable Pydantic configuration models for library components.
They are the main customization mechanism and can themselves be loaded from
sources. Defaults keep simple usage small; settings make advanced workflows
versionable and explicit.

Important settings families:

- source settings.
- source executor settings.
- parser settings.
- template engine settings.
- compiler and renderer settings.
- manager/cache settings.

### Engine

Template engine adapters live in `templisafe.engine`.

A `TemplateEngine` extracts undeclared variables and renders strings. Engines
adapt third-party rendering libraries and hide their APIs from the rest of the
system. Jinja is the default, Django is available, and custom engines can be
integrated by implementing the engine abstraction.

### Template Domain

Domain models and operations live in `templisafe.template`.

The core value objects are:

- `Template`: template string plus referenced variables.
- `Schema`: Pydantic model representing accepted variables.
- `CompilationSpec`: successful compiled template and schema.
- `Compilation`: compile outcome, diagnostics and optional spec.
- `Binding`: one value for one variable.
- `Variant`: named collection of bindings.
- `VariantSet`: collection of variants.
- `Parameterization`: one rendered output for one variant.
- `RenderingSpec`: rendered outputs indexed by variant name.
- `Rendering`: validation/rendering outcome, diagnostics and optional rendered
  spec.
- `Build`: combined compilation and rendering result.
- `Outcome`: `SUCCESS`, `WARNING` or `ERROR`.
- `Diagnostic`: structured result message.

`Compiler` checks template variables against the schema and produces
`Compilation`.

`Renderer` validates variants against the compiled schema, applies defaults, and
renders parameterizations through a template engine.

The domain layer should operate on already loaded domain models, not on sources
or raw configuration files.

### Handler

Handlers live in `templisafe.handler`.

`OutcomeHandler` applies the caller's `DiagnosticPolicy` at the API boundary.
The supported policies are:

- `ignore`: never raise for warning/error outcomes; return diagnostics.
- `log`: warn on warnings, raise on errors.
- `strict`: raise on warnings and errors.

`DiagnosticHandler` is lower-level diagnostic behavior used by infrastructure
components such as pools.

## Task Flows

### Compile

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

### Validate

```text
RenderingBundle(render=False)
  -> SourceService
  -> DataService
  -> ConfigService
  -> SettingsService
  -> ComponentService
  -> ResourceService
  -> Rendering
```

Validation creates a `VariantSet`, resolves a `Renderer`, and validates variant
bindings against the compiled schema without rendering template output.

### Render

```text
RenderingBundle(render=True)
  -> SourceService
  -> DataService
  -> ConfigService
  -> SettingsService
  -> ComponentService
  -> ResourceService
  -> Rendering
```

Rendering follows the validation path, resolves a `TemplateEngine`, and renders
successful parameterizations.

### Build

```text
BuildBundle
  -> compile subtask
  -> render subtask
  -> Build
```

Build reuses the same orchestrated machinery as compile and render. If the
compile subtask fails, rendering is skipped and the returned `Build` carries the
compilation diagnostics.

## Construction Pattern

For extensible components, the recurring pattern is:

- `Settings`: immutable configuration.
- `Factory`: creates concrete implementation from settings.
- `Manager`: optional cache over factory-created objects.
- `Resolver`: accepts an existing object, settings or default.
- `Assembler`: wires default resolver graphs.
- `Provider`: service-facing facade.
- `Service`: task-bundle transformation stage.

This explicit pattern is intentionally a little verbose. It makes extension
points visible and keeps user-facing orchestration separate from implementation
selection.

## Extension Points

### Add a Source

1. Create a `SourceSettings` subclass.
2. Register its `SourceKind`.
3. Implement a `Source` subclass.
4. Add it to `SourceFactory`.
5. Add tests for content type resolution, lifecycle and executor behavior.

### Add a Template Engine

1. Add a `TemplateEngineKind`.
2. Implement `TemplateEngine`.
3. Register it in `TemplateEngineFactory`.
4. Add extraction and rendering tests.

### Add a Config Format

1. Add a `ContentType`.
2. Implement `ConfigParser`.
3. Register it in `ConfigParserFactory`.
4. Add parser and source integration tests.

## Architectural Invariants

- Public API methods construct tasks; they do not perform low-level work.
- Services transform bundles and delegate specialized work to providers.
- Providers apply components methods on appropriate resources and return the results.
- Sources only read content.
- Executors only coordinate source reads.
- Parsers only parse content or configuration.
- Compiler and renderer only operate on domain models.
- Outcome handling happens at the API boundary after task execution.
- Domain models remain independent from IO concerns.
