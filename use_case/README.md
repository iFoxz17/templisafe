# templisafe – use cases

This folder contains practical, end-to-end examples demonstrating how **templisafe** can be applied to real-world problems where **safety, correctness and flexibility** in templating are critical.

Each use case focuses on a concrete scenario and shows how templisafe builds on top of existing template engines to provide **schema-driven validation**, **safe parameterization** and **multi-variant rendering**.

**Use Case 1** provides a more didactic introduction, covering all the core concepts of the library, whereas Use **Case 2** assumes familiarity with these basics and focuses on advanced scenarios.

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

### 2. Safe Infrastructure-as-Code (IaC) Definitions

This use case demonstrates how `templisafe` can be applied to **Infrastructure-as-Code (IaC)** scenarios, where the same resource definition must be rendered differently across environments such as **development**, **pre-production**, and **production**.

**Demonstrates:**
- Defining infrastructure templates once  
- Using a shared schema to enforce constraints  
- Creating environment-specific variants (dev / preprod / prod)  
- Applying different limits, sizes or flags per environment  
- Rendering validated configurations for each environment  

**Benefits:**
- Prevents unsafe or invalid infrastructure configurations  
- Enforces environment-specific constraints declaratively  
- Reduces duplication while maintaining strict validation  
- Increases confidence when promoting configurations across environments  

**Typical applications:**
- Cloud resource definitions  
- Deployment manifests  
- Configuration templates for CI/CD pipelines

---

## How to Use These Examples

Each use case folder contains:
- Template definitions
- Schema definitions
- Variants definitions
- A runnable example (notebook)

You can run them:
- As standalone examples
- As references for building your own workflows
- As test cases when integrating `templisafe` into larger systems

---

## Notes

- All examples rely only on the public API of the library
- Defaults configurations are used wherever possible to keep examples simple and readable

For deeper details about the underlying abstractions, refer to the main [documentation](/doc).