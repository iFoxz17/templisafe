# Use case 1: Safe Query Parameterization

This folder contains a [**notebook**](./safe_query_parameterization.ipynb) that demonstrates how to use **templisafe** to safely parameterize SQL queries.

The example builds an orders report query with a dynamic select list, typed filters, defaults, and multiple variants.
The SQL template also imports a Jinja macro through a loader configured with `TemplateEngineSettings`.

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

- [**`template.sql.j2`**](./resources/template.sql.j2)
  The SQL query template, using Jinja-style placeholders for variables and importing a Jinja macro.

- [**`macros/order_filters.sql.j2`**](./resources/macros/order_filters.sql.j2)
  A Jinja macro used by the template to render the optional customer filter.

- [**`schema.yaml`**](./resources/schema.yaml)
  Defines the variables used in the template, including types and default values.

- [**`variants1.yaml`**](./resources/variants1.yaml)
  Contains two explicit parameterizations: `recent_paid_orders` and `high_value_orders`.

- [**`variants2.yaml`**](./resources/variants2.yaml)
  Contains a single parameterization `all_paid_orders` that relies on defaults from the schema.
