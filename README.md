# templisafe

**Safe, flexible and fully configurable templating for Python.**

**`templisafe` is not another template engine**. Instead, it is a high-level framework built **on top of existing template engines** to simplify and secure template management. It generates schemas for template variables, validates parameterizations and renders templates safely and efficiently. It is designed to be flexible, agnostic to both template engines and configuration languages, and fully ready for cloud-based sources.

---

## Key Principles

- **Engine and Configuration Agnostic:** Works with any template engine (default is [`Jinja`](https://github.com/pallets/jinja)) and any configuration language (`YAML`, `JSON`, `TOML`, `XML`, ...).  
- **Schema Generation with Pydantic:** Uses [`pydantic`](https://pydantic-docs.helpmanual.io/) to automatically generate schemas for template variables, ensuring type safety, constraints and validation.
- **Flexible Source Handling:** Accepts inline, local and remote sources (`S3`, `Azure Blob`, `GCP Cloud Storage`, ...), abstracting all reading methods and allowing the same API to handle any source type transparently.  
- **Concurrent and Efficient:** Uses `asyncio` to load and process multiple sources in parallel, minimizing latency when handling cloud sources.
- **Fully Configurable:** Every aspect of the library can be configured. Defaults are provided so you can start simple while keeping full flexibility for advanced use cases.  
- **Simple and Well-Documented API:** Practical examples and clear method interfaces make templating easy and safe.

---

## Installation

```bash
pip install templisafe
```

## Quick Start
```python
from templisafe import (
    SourceSettings,
    ContentType,
    TemplaterFactory, 
    Templater,
    Build
) 

# Define a template source settings (can be inline, local or cloud)
template_source_settings: SourceSettings = SourceSettings.create(
    kind="inline", 
    content="Hello {{ name }}!", 
    content_type=ContentType.TEXT
)

# Define a schema source settings (can be inline, local or cloud)
schema_content: str = """
schema:
    name: str
"""
schema_source_settings: SourceSettings = SourceSettings.create(
    kind="inline", 
    content=schema_content,
    content_type=ContentType.YAML
)

# Define one or more variants source settings (can be inline, local or cloud)
variants_source_settings: SourceSettings = SourceSettings.create(
    kind="inline", 
    content="""
    {
        "variants": [
            {
                "name": "hello_world",
                "bindings": {
                    "name": "World"
                }
            },
            {
                "name": "hello_italy",
                "bindings": {
                    "name": "Italy"
                }
            }
        ]
    }
    """,
    content_type=ContentType.JSON
)

# Create a templater instance with default settings
templater: Templater = TemplaterFactory().create()

# Build the template (compile the schema and render all variants)
build: Build = templater.build(
    template_source=template_source_settings,
    variants_sources=[variants_source_settings],
    schema_source=schema_source_settings
    )

# Access rendered output
for name, param in build.rendering.rendered.mapping.items():
    print(f"{name}: '{param.rendered_str}'")       

# Prints:
# "hello_world: 'Hello World!'"
# "hello_italy: 'Hello Italy!'"
```

See the proposed [use cases](use_case) for more advanced examples.


## Core Abstractions

**templisafe** introduces several key abstractions to manage templates, parameterizations and rendering safely:

### Template & Compilation

- **`Template`** – Represents the template string and the set of referenced variables.  
- **`Schema`** – A Pydantic model describing the variables of a template.  
- **`CompilationSpec`** – Combines a template with its schema.  
- **`Compilation`** – Contains the result of compilation, including diagnostics messages and access to the `CompilationSpec`.

### Variants & Bindings

- **`Binding`** – Represents a value assigned to a template variable.  
- **`Variant`** – A set of bindings representing a specific configuration of variables.  
- **`VariantSet`** – Holds multiple variants for different parameterizations.
- **`Parameterization`** – Combines a `Variant` with its rendered output.

### Rendering

- **`RenderingSpec`** – Represents a rendered template along with all parameterizations.  
- **`Rendering`** – Contains the outcome, messages, diagnostics and access to the `RenderingSpec`.

### Build

- **`Build`** – Represents a complete build workflow, including both compilation and rendering results. Provides a unified `outcome` for the entire process.

Access the [full documentation](doc) for more information.

## Configuration

All configurations are optional. You can override any aspect, including:

- Compiler settings
- Renderer settings
- Template engine settings
- Loader settings for templates, schemas or variants
- Diagnostic policies

Default configurations make it ready to use with minimal setup, while still providing full control when needed.

## Advanced Usage

Explore realistic applications of the library in the [use case folder](use_case).


## Contributing

Contributions to **templisafe** are welcome!  

Please see the [contributing folder](contributing) for detailed guidelines on how to:

- Report issues or suggest new features  
- Set up a development environment  
- Run tests and check code quality  
- Submit pull requests  

We appreciate your help in making **templisafe** more robust, flexible and reliable!


## License

templisafe is open-source software licensed under the MIT License. See [the license](LICENSE) for more details.