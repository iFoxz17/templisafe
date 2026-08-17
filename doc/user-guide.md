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

Install optional extras only when needed:

```bash
pip install "templisafe[http-async]"    # Async sources support
pip install "templisafe[s3]"            # S3 sources support
```

The development extra includes test and quality tooling:

```bash
pip install -e ".[dev]"
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
- `validate(compiled, variants)`: loads variants and validates them without
  rendering.
- `render(compiled, variants)`: loads variants, validates them against a
  `CompilationSpec`, renders successful variants and returns a `Rendering`.
- `build(template, variants, schema=None)`: performs compile and render in a
  single call and returns a `Build`.

Every workflow accepts direct values, public input models, concrete sources or
settings objects. `SourceSettings` is the most portable API because it keeps
inputs serializable and easy to move to files later.

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

Inline and local sources are the simplest path. HTTP and AWS sources are useful
when templates, schemas, variants or settings are stored remotely. Async HTTP
support is optional and loaded lazily.

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
for rendering the final string. Engine-specific features remain available
through engine settings. For example, a Jinja loader can be passed through
`TemplateEngineSettings.config` (see [this use case](example\1_safe-query-parameterization) for more details).

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

Schemas can also be built dynamically with `SchemaInput` and `VariableInput`
instead of being read from configuration files.

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

Implicit unnamed form:

```yaml
variants:
  name: World
```

During validation and rendering:

- missing required bindings produce errors.
- invalid binding values produce errors.
- extra bindings produce warnings.
- defaults from the schema are used for omitted optional/defaulted fields.

Variants can also be built dynamically with `VariantInput` and
`VariantSetInput`.

## Results

The main result objects are:

- `Compilation`: compilation outcome, diagnostics and `CompilationSpec` when
  compilation succeeds.
- `Rendering`: validation/rendering outcome, diagnostics and rendered
  parameterizations when rendering succeeds.
- `Build`: combined compilation and rendering result.
- `Outcome`: `SUCCESS`, `WARNING` or `ERROR`.
- `Diagnostic`: structured message with level, name and optional index.

Access a successful compilation with `compilation.compiled` and a successful
rendering with `rendering.rendered`. If the result failed, those accessors raise
the corresponding failure exception.

When `build` compilation fails and the diagnostic policy allows returning error
outcomes, rendering is skipped and the returned `Build` carries the compilation
diagnostics.

## Diagnostics

`TemplaterFactory().create(diagnostic_policy=...)` controls how warning and
error outcomes are handled.

Supported policies:

- `ignore`: never raise for warning/error outcomes; return diagnostics.
- `log`: warn on warnings, raise on errors.
- `strict`: raise on warnings and errors.

Use `ignore` when programmatic access to diagnostics is more useful than
exceptions.

```python
templater = TemplaterFactory().create(diagnostic_policy="ignore")
compilation = templater.compile(template=template, schema=schema)

if compilation.outcome.name == "ERROR":
    for diagnostic in compilation.diagnostics:
        print(diagnostic.message)
```

## Settings

Settings configure library components:

- source execution strategy and retry policy.
- template engine.
- template parser.
- schema parser.
- variant parser.
- compiler.
- renderer.
- diagnostic policy.

Factory-level settings configure defaults for a `Templater` instance. Per-call
settings can override those defaults. Settings can be provided directly as
settings objects or loaded from sources when a workflow accepts per-call
settings.

Defaults are provided for every component, so simple workflows require little
configuration. Advanced workflows can move settings into versioned files or
remote sources.

## Dynamic Inputs

Configuration files are not required. Public input models can be used when
templates, schemas or variants are generated at runtime.

```python
from templisafe import SchemaInput, VariableInput, VariantInput

schema = SchemaInput(
    schema={
        "name": "str",
        "score": VariableInput(type="int", constraints={"ge": 0}),
    }
)

variant = VariantInput(name="run_1", bindings={"name": "Ada", "score": 42})

build = templater.build(
    template="Name={{ name }} Score={{ score }}",
    schema=schema,
    variants=variant,
)
```

## When To Use Templisafe

Use templisafe when templates are part of a repeatable system and you want:

- explicit variable contracts.
- typed and constrained parameterizations.
- reusable variant files.
- pluggable storage for templates and configuration.
- clear diagnostics before rendering reaches production workflows.

For a one-off template rendered from an in-memory dictionary, calling the
template engine directly is usually enough.
