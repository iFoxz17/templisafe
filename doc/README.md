# Documentation

## Public Workflow

The public API is centered on `TemplaterFactory().create()` and the resulting
`Templater` instance:

1. `compile(template, schema)` reads sources, parses the template and optional
   schema, then returns a `Compilation`.
2. `render(compiled, variants)` reads one or more variant sources, validates the
   bindings and renders each parameterization.
3. `validate(compiled, variants)` performs validation without rendering.
4. `build(template, variants, schema)` runs compile and render as one workflow
   and returns a `Build`.

Sources are resolved through `SourceSettings` or concrete `Source` instances.
Inline and local sources are the stable first-version path. HTTP and AWS source
components are present as lower-level building blocks and have dedicated tests.

## Package Map

- `templisafe.source`: source abstractions and source settings.
- `templisafe.executor`: synchronous source execution strategies.
- `templisafe.parser`: config, schema, template and variant parsing.
- `templisafe.engine`: template engine adapters, with Jinja as default.
- `templisafe.template`: template model, compiler and renderer.
- `templisafe.provider` and `templisafe.service`: lower-level composition helpers
  used by the internal architecture.

## Core Abstractions

**templisafe** introduces several key abstractions to manage templates, parameterizations, and rendering safely:

### Template & Compilation

- **`Template`** – Represents the template string and the set of referenced variables.  
- **`Schema`** – A Pydantic model describing the variables of a template.  
- **`CompilationSpec`** – Combines a template with its schema.  
- **`Compilation`** – Contains the result of compilation, including diagnostics, messages, and access to the `CompilationSpec`.

### Variants & Bindings

- **`Binding`** – Represents a value assigned to a template variable.  
- **`Variant`** – A set of bindings representing a specific configuration of variables.  
- **`VariantSet`** – Holds multiple variants for different parameterizations.  
- **`Parameterization`** – Combines a `Variant` with its rendered output.

### Rendering

- **`RenderingSpec`** – Represents a rendered template along with all parameterizations.  
- **`Rendering`** – Contains the outcome, messages, diagnostics, and access to the `RenderingSpec`.

### Build

- **`Build`** – Represents a complete build workflow, including both compilation and rendering results. Provides a unified `outcome` for the entire process.

### Outcome & Diagnostics

- **`Outcome`** – Enum describing success, warning, or error states.  
- **`Diagnostic`** – Contains messages for specific variables during compilation or rendering.

---

## Concepts

- **Variant:** A set of `Binding`s providing values for template variables.  
- **Parameterization:** A named variant which identifies a specific configuration for the template.  
- **Binding:** A single value assignment for a variable in a variant.  
- **CompilationSpec & RenderingSpec:** Internal representations for compiled templates and rendered templates with parameterizations.  
- **Compilation & Rendering:** The results of compiling and rendering templates, including messages, outcomes, and diagnostics.  
- **Build:** The full workflow result combining compilation and rendering.  

These abstractions allow **templisafe** to validate templates, enforce schema constraints, and safely generate multiple parameterizations automatically.

---
