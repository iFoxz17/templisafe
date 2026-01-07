from sqltemplater.query.query_model import (
    QCompilationSpec,
    QTemplate,
    QSchema,
    QVar,
    QOutcome,
    QDiagnostic,
    QCompilation
)

class QueryCompiler:
    """Compiles a query template against a schema, producing a QCompilation with diagnostics."""

    __slots__: tuple[str, ...] = ()

    def _create_empty_schema(self, var_names: set[str]) -> QSchema:
        return QSchema(
            vars=[
                QVar(index=i, name=p, type_=object, default=None)
                for i, p in enumerate(var_names)
            ]
        )

    def compile(
        self,
        template: QTemplate,
        schema: QSchema | None = None,
    ) -> QCompilation:
        """Compile a template with an optional schema, returning a QCompilation with warnings/errors."""

        template_vars: set[str] = template.vars

        if schema is None:
            schema = self._create_empty_schema(template_vars)
            return QCompilation(
                outcome=QOutcome.SUCCESS,
                message="Query successfully compiled with empty schema",
                _spec=QCompilationSpec(template=template, schema=schema),
            )

        schema_vars: set[str] = schema.names

        undeclared_vars: set[str] = template_vars - schema_vars
        unused_vars: set[str] = schema_vars - template_vars

        diagnostics: list[QDiagnostic] = []
        outcome = (
            QOutcome.ERROR
            if undeclared_vars
            else QOutcome.WARNING
            if unused_vars
            else QOutcome.SUCCESS
        )

        # Unused variables (provided in schema but not in template)
        for var_name in sorted(unused_vars):
            var: QVar = schema[var_name]
            diagnostics.append(
                QDiagnostic(
                    level=QOutcome.WARNING,
                    message=f"Unused variable: '{var_name}'",
                    name=var.name,
                    index=var.index
                )
            )

        # Undeclared parameters (in template but missing in schema)
        for var_name in sorted(undeclared_vars):
            diagnostics.append(
                QDiagnostic(
                    level=QOutcome.ERROR,
                    message=f"Undeclared variable: '{var_name}'",
                    name=var_name,
                    index=None
                )
            )

        if outcome is QOutcome.ERROR:
            return QCompilation(
                outcome=outcome,
                message="Query compilation failed",
                _spec=None,
                diagnostics=tuple(diagnostics),
            )

        return QCompilation(
            outcome=outcome,
            message="Query successfully compiled with schema",
            _spec=QCompilationSpec(template=template, schema=schema),
            diagnostics=tuple(diagnostics),
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
