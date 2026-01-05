from dataclasses import dataclass


from sqltemplater.query.query_model import (
    CompiledQuery,
    QueryTemplate,
    QuerySchema,
    ParamSchema,
    BuildOutcome,
    BuildDiagnostic,
    CompilationResult
)

class QueryCompiler:
    __slots__ = ()

    def _create_empty_schema(self, params: set[str]) -> QuerySchema:
        return QuerySchema(
            params=[
                ParamSchema(index=i, name=p, type_=object, default=None)
                for i, p in enumerate(params)
            ]
        )

    def compile(
        self,
        template: QueryTemplate,
        schema: QuerySchema | None = None,
    ) -> CompilationResult:

        template_params: set[str] = set(template.params)

        if schema is None:
            schema = self._create_empty_schema(template_params)
            return CompilationResult(
                outcome=BuildOutcome.SUCCESS,
                message="Query successfully compiled with empty schema",
                compiled_query=CompiledQuery(template=template, schema=schema),
            )

        schema_params: set[str] = set(schema.names)

        undeclared: set[str] = template_params - schema_params
        unused: set[str] = schema_params - template_params

        diagnostics: list[BuildDiagnostic] = []
        outcome = (
            BuildOutcome.ERROR
            if undeclared
            else BuildOutcome.WARNING
            if unused
            else BuildOutcome.SUCCESS
        )

        # Unused parameters (provided in schema but not in template)
        for param in sorted(unused):
            param_schema: ParamSchema = schema[param]
            diagnostics.append(
                BuildDiagnostic(
                    level=BuildOutcome.WARNING,
                    message=f"Unused parameter: '{param}'",
                    param=param,
                    index=param_schema.index
                )
            )

        # Undeclared parameters (in template but missing in schema)
        for param in sorted(undeclared):
            diagnostics.append(
                BuildDiagnostic(
                    level=BuildOutcome.ERROR,
                    message=f"Undeclared parameter: '{param}'",
                    param=param,
                    index=None
                )
            )

        if outcome is BuildOutcome.ERROR:
            return CompilationResult(
                outcome=outcome,
                message="Query compilation failed",
                compiled_query=None,
                diagnostics=tuple(diagnostics),
            )

        return CompilationResult(
            outcome=outcome,
            message="Query successfully compiled with schema",
            compiled_query=CompiledQuery(template=template, schema=schema),
            diagnostics=tuple(diagnostics),
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
