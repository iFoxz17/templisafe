# Use case 1: Safe Query Parameterization

This folder contains a [**notebook**](./safe_query_parameterization.ipynb) that demonstrates how to use **templisafe** to safely parameterize SQL queries.

## Scope

The notebook covers:

- Main objects needed for library usage.
- Defining a SQL query as a template.
- Generating a schema for all template variables.
- Creating multiple variants (parameterizations) for the query.
- Rendering validated queries automatically, applying defaults where needed.

The goal is to **prevent runtime errors**, enforce type safety and make query generation explicit, testable and auditable.

## Resources

The example uses the following files:

- [**`template.sql.j2`**](./template.sql.j2)
  The SQL query template, using Jinja-style placeholders for variables.

- [**`schema.yaml`**](./schema.yaml)
  Defines the variables used in the template, including types and default values.

- [**`variants1.yaml`**](./variants1.yaml)
  Contains two explicit parameterizations: `adults_only` and `minors_only`.

- [**`variants2.yaml`**](./variants2.yaml)
  Contains a single parameterization `all_ages` that relies on defaults from the schema.