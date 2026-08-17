# templisafe – use cases

This folder contains practical, end-to-end examples demonstrating how **templisafe** can be applied to real-world problems where **safety, correctness and flexibility** in templating are critical.

Each use case focuses on a concrete scenario and shows how templisafe builds on top of existing template engines to provide **schema-driven validation**, **safe parameterization** and **multi-variant rendering**.

**Use Case 1** provides a more didactic introduction, covering all the core concepts of the library, whereas **Use Case 2** assumes familiarity with these basics and focuses on advanced scenarios.

---

## Use Cases Overview

### 1. Safe Query Parameterization

This use case illustrates how `templisafe` enables safe and reliable parameterization of **SQL queries** using templates.

**Demonstrates:**
- Defining a query as a template  
- Generating a schema for template variables automatically  
- Rendering multiple parameterizations safely  
- Preventing common errors such as undeclared, unused, or invalid variables  

**Benefits:**
- Eliminates runtime errors from missing or mismatched variables  
- Enforces type safety on query parameters  
- Makes query generation explicit, testable, and auditable  

**Typical applications:**
- SQL query generation  
- Analytics and reporting pipelines  
- Search and filtering systems

---

## Notes

- All examples rely only on the public API of the library
- Defaults configurations are used wherever possible to keep examples simple and readable

For deeper details about the underlying abstractions, refer to the main [documentation](/doc).