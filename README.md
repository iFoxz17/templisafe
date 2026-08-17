# templisafe

[![Dev CI/CD](https://github.com/iFoxz17/templisafe/actions/workflows/dev.yml/badge.svg?branch=dev)](https://github.com/iFoxz17/templisafe/actions/workflows/dev.yml)
[![Main CI/CD](https://github.com/iFoxz17/templisafe/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/iFoxz17/templisafe/actions/workflows/main.yml)
[![Release CI/CD](https://github.com/iFoxz17/templisafe/actions/workflows/release.yml/badge.svg?branch=release)](https://github.com/iFoxz17/templisafe/actions/workflows/release.yml)

Template-as-Code for safe, validated rendering workflows.

`templisafe` is not another template engine. It is a framework built around
template engines such as Jinja or Django to make templating safer, more
repeatable and easier to operate.

The project applies an Infrastructure-as-Code mindset to templating: templates,
schemas, concrete values and execution settings can be described as explicit
resources, loaded from configurable sources, validated before rendering and
processed through a minimal public API.

## Why

Templating is often simple at the beginning: one template string, one dictionary
of values, one render call. It becomes harder to control when templates are used
for SQL queries, configuration files, prompts, reports, messages, deployment
manifests or any other generated artifact that needs consistency.

`templisafe` helps when you want:

- template variables to have an explicit contract.
- values to be validated before rendering.
- multiple parameterizations of the same template.
- schemas and variants to live in normal configuration files.
- templates and values to be loaded from files, HTTP endpoints, cloud services
  or custom sources.
- a stable API that does not depend on one template engine or one configuration
  language.

## Core Idea

A templisafe workflow is built from five concepts.

**Template**

The target text to produce. It can represent any file or text-based artifact:
SQL, Markdown, HTML, prompts, configuration files or plain text. The rendering
syntax is delegated to a template engine.

**Schema**

The contract associated with a template. A schema defines the variables accepted
by the template, including their types and optional constraints. Schema files are
parsed from supported configuration languages and validation is powered by
**Pydantic**.

**Variant**

A concrete set of values for a template. One template can have many variants,
so the same template can be rendered for different environments, customers,
queries or use cases. Variants are also configuration resources, so they can be
written and versioned in supported formats such as **YAML**, **JSON**, **TOML** or **XML**
without changing the templating workflow.

**Source**

The abstraction used to load templates, schemas, variants and settings. Sources
can be inline values, local files, HTTP resources, cloud resources or custom
implementations provided by the user. In every case, the library only needs a
source implementation able to return content through the `read` method.

**Settings**

The configuration layer used to customize library components. Settings can tune
sources, parsers, template engines, executors, compilers and renderers. They can
be passed directly or loaded from sources, so advanced behavior can be stored in
files and versioned together with templates, schemas and variants. Defaults are
provided for every component, so simple workflows require little configuration.

## Design Principles

- Template-as-Code: templates, schemas and variants are treated as explicit,
  versionable resources.
- Engine independence: Jinja is supported by default, Django is available, and
  custom engines can be integrated through inheritance.
- Configuration independence: schemas, variants and settings can be expressed in
  supported configuration formats without changing the public workflow.
- Source independence: the API works with source abstractions rather than only
  local files or in-memory strings.
- Progressive configuration: defaults keep the simple path small, while the
  `Settings` abstraction allows any component to be customized and versioned.
- Minimal public API: compile, validate and render are the fundamental
  operations; build combines them into one workflow.

## Supported Capabilities

| Area | Supported |
| --- | --- |
| Template engines | Jinja by default, Django support, custom engines |
| Schema / variant formats | YAML, JSON, TOML, XML |
| Sources | Inline, local files, HTTP resources and custom sources |
| Validation | Pydantic-backed types, defaults and constraints |
| Customization | Versionable settings for sources, parsers, engines, executors, compilers and renderers |

## Installation

```bash
pip install templisafe
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
  - name: italy
    bindings:
      name: Italy
  - name: world
    bindings:
      name: World
""",
    content_type=ContentType.YAML,
)

templater = TemplaterFactory().create()
build = templater.build(template=template, schema=schema, variants=variants)

for name in sorted(build.rendering.rendered.names):
    print(build.rendering.rendered[name].rendered_str)
```

Output:

```text
Hello Italy!
Hello World!
```

Schemas can also define constraints that are enforced before rendering:

```yaml
schema:
  score:
    type: int
    constraints:
      gt: 0
      lt: 101
  name:
    type: str
    constraints:
      max_length: 40
```

Advanced configuration can use the same source model. Defaults are available for
every component, but settings can be moved to files or remote sources when a
workflow needs to be versioned more explicitly:

```python
engine_settings = SourceSettings.create(
    kind="inline",
    content="engine_kind: jinja",
    content_type=ContentType.YAML,
)

build = templater.build(
    template=template,
    schema=schema,
    variants=variants,
    template_engine=engine_settings,
)
```

## Public API

The public API is centered on the `Templater` abstraction:

- `compile(template, schema=None)` compiles a template and its optional schema.
- `validate(compiled, variants)` validates variant values without rendering.
- `render(compiled, variants)` validates and renders the variants.
- `build(template, variants, schema=None)` runs compile, validate and render as one
  workflow.

Inputs can be provided directly, through concrete source objects or through
serializable `SourceSettings`.

## When Not To Use It

For a one-off template rendered from an in-memory dictionary, calling the
template engine directly is probably enough. `templisafe` is useful when
templates become reusable assets and need contracts, validation, multiple
variants, configurable sources or repeatable workflows.

## Documentation

- [User guide](doc/user-guide.md): public API, source types, schemas, variants
  and diagnostics.
- [Architecture](doc/architecture.md): internal modules, task pipeline,
  services, providers and extension points.
- [Examples](example): practical examples.
- [Contributing](contributing): development setup, tests and contribution
  workflow.

## Development

```bash
pip install -e ".[dev]"
python -m pytest -c test/pytest.ini -q
python -m ruff check .
python -m mypy src
```

## License

templisafe is open-source software licensed under the MIT License. See [the license](LICENSE) for more details.
