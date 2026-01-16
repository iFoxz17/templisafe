# Documentation

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
