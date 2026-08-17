# User Guide

`templisafe` is a high-level templating library built on top of existing
template engines. It reads templates, schemas and variants from configurable
sources, validates the provided bindings, and renders one or more
parameterizations safely.

The public API is intentionally small: most users only need
`TemplaterFactory().create()` and the resulting `Templater` instance.

## Installation

```bash
pip install templisafe
```

Install the async HTTP extra only when using async HTTP sources:

```bash
pip install "templisafe[http-async]"
```

## Quick Start

```python
from templisafe import ContentType, SourceSettings, TemplaterFactory

template = SourceSettings.create(
    kind="inline",
    content="Hello {{ name }}!",
    content_type=ContentType.TEXT,
)

schema = SourceSettings.create(
    kind="inline",
    content="""
schema:
  name: str
""",
    content_type=ContentType.YAML,
)

variants = SourceSettings.create(
    kind="inline",
    content="""
variants:
  - name: world
    bindings:
      name: World
""",
    content_type=ContentType.YAML,
)

templater = TemplaterFactory().create()
build = templater.build(template=template, schema=schema, variants=variants)

print(build.rendering.rendered["world"].rendered_str)
```

## Public Workflow

`Templater` exposes four workflows:

- `compile(template, schema=None)`: loads a template and optional schema,
  extracts variables and returns a `Compilation`.
- `render(compiled, variants)`: loads variants, validates them against a
  `CompilationSpec`, renders successful variants and returns a `Rendering`.
- `validate(compiled, variants)`: loads variants and validates them without
  rendering.
- `build(template, variants, schema=None)`: performs compile and render in a
  single call and returns a `Build`.

Every workflow accepts concrete objects or settings objects. The stable public
entry point is the `SourceSettings` based API because it keeps inputs
serializable and portable.

## Sources

Sources describe where templisafe should read input data from. A source produces
a string payload and a `ContentType`.

Available source settings:

- `InlineSourceSettings`: content embedded directly in the settings object.
- `LocalSourceSettings`: content read from a local file path.
- `HttpSourceSettings`: content read from HTTP endpoints.
- `AwsS3BucketSourceSettings`: content read from an S3 object.
- `AwsSecretsManagerSourceSettings`: content read from AWS Secrets Manager.
- `AwsSsmParameterSourceSettings`: content read from AWS Systems Manager
  Parameter Store.
- `AwsDynamoDBSourceSettings`: content read from DynamoDB.

Inline and local sources are the simplest and most stable path for local usage.
HTTP and AWS sources are available for remote configuration and cloud-hosted
templates.

## Content Types

`ContentType` tells templisafe how to interpret source payloads:

- `TEXT`: raw template text.
- `YAML`: YAML configuration.
- `JSON`: JSON configuration.
- `TOML`: TOML configuration.
- `XML`: XML configuration.

Templates are usually `TEXT`. Schemas, variants and settings are usually YAML,
JSON, TOML or XML.

## Templates

Templates are rendered by a configured template engine. Jinja is the default
engine. Django templates are also supported.

```python
from templisafe import TemplateEngineSettings

engine_settings = TemplateEngineSettings.create(engine_kind="jinja")
templater = TemplaterFactory().create(template_engine_settings=engine_settings)
```

The engine is responsible for extracting variable names from the template and
for rendering the final string.

## Schemas

A schema declares the variables a template accepts. Templisafe converts schema
configuration into a dynamic Pydantic model, so bindings are validated with
Pydantic's normal type and constraint rules.

```yaml
schema:
  name: str
  age:
    type: int
    constraints:
      ge: 0
  country:
    type: str
    default: Italy
```

Supported base types include `bool`, `int`, `float`, `str`, `list`, `dict`,
`date`, `datetime`, `object`, and nested forms such as `optional[str]`,
`list[int]` and `dict[str, int]`.

During compilation:

- template variables missing from the schema produce errors.
- schema variables unused by the template produce warnings.
- a missing schema creates an implicit permissive schema from the template
  variables.

## Variants

A variant is a named set of bindings for template variables. A variant file can
define one or more variants.

Explicit form:

```yaml
variants:
  - name: english
    bindings:
      name: World
  - name: italian
    bindings:
      name: Italia
```

Implicit named form:

```yaml
variants:
  english:
    name: World
  italian:
    name: Italia
```

During validation and rendering:

- missing required bindings produce errors.
- invalid binding values produce errors.
- extra bindings produce warnings.
- defaults from the schema are used for omitted optional/defaulted fields.

## Results

The main result objects are:

- `Compilation`: compilation outcome, diagnostics and `CompilationSpec`.
- `Rendering`: rendering or validation outcome, diagnostics and rendered
  parameterizations when rendering succeeds.
- `Build`: combined compilation and rendering result.
- `Outcome`: `SUCCESS`, `WARNING` or `ERROR`.
- `Diagnostic`: structured message with level, name and optional index.

Access a successful compilation with `compilation.compiled` and a successful
rendering with `rendering.rendered`. If the result failed, those accessors raise
the corresponding failure exception.

## Diagnostics

`TemplaterFactory().create(diagnostic_policy=...)` controls how warning and
error outcomes are handled.

Supported policies:

- `log`: log diagnostics.
- `warn`: emit Python warnings.
- `raise`: raise failures for error outcomes.
- `ignore`: do not emit diagnostics.

## Configuration

Factory-level settings configure defaults for a `Templater` instance. Per-call
settings can override those defaults.

Configurable areas:

- source execution strategy and retry policy.
- template engine.
- template parser.
- schema parser.
- variant parser.
- compiler.
- renderer.
- diagnostic policy.

Settings can be provided directly as settings objects or loaded from sources
when a workflow accepts per-call settings.

## When To Use Templisafe

Use templisafe when templates are part of a repeatable system and you want:

- explicit variable contracts.
- typed and constrained parameterizations.
- reusable variant files.
- pluggable storage for templates and configuration.
- clear diagnostics before rendering reaches production workflows.
