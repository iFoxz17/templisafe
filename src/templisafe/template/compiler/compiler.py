from typing import Any

from pydantic import BaseModel

from templisafe.core.metadata import metadata_value
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.template.template_model import (
    Compilation,
    CompilationSpec,
    Diagnostic,
    Outcome,
    Schema,
    Template,
)


class Compiler:
    """Compiles a template against a schema, producing a compilation result with diagnostics."""

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self, settings: CompilerSettings) -> None:
        self._settings = settings

    def _extract_index(self, model_type: type[BaseModel], var_name: str) -> int | None:
        field = model_type.model_fields[var_name]
        index_value = metadata_value(field.metadata, self._settings.index_key)
        index: int | None = index_value if isinstance(index_value, int) else None
        return index

    def _create_empty_schema(self, var_names: set[str]) -> Schema:
        # Lazy imports since this method could be used rarely
        from pydantic import Field, create_model

        fields: dict[str, Any] = {name: (object, Field(None)) for name in var_names}
        model_cls: type = create_model("EmptySchema", **fields)
        return Schema(model_cls=model_cls)

    def compile(
        self,
        template: Template,
        schema: Schema | None = None,
    ) -> Compilation:
        """Compile a template with an optional schema, returning a `Compilation` with diagnostics."""

        template_vars: set[str] = template.vars

        if schema is None:
            schema = self._create_empty_schema(template_vars)
            return Compilation(
                outcome=Outcome.SUCCESS,
                message="Query successfully compiled with empty schema",
                _spec=CompilationSpec(template=template, schema=schema),
                diagnostics=(),
            )

        model_cls: type[BaseModel] = schema.model_cls
        schema_fields: dict[str, Any] = schema.model_cls.model_fields
        schema_vars: set[str] = set(schema_fields.keys())

        undeclared_vars: set[str] = template_vars - schema_vars
        unused_vars: set[str] = schema_vars - template_vars

        diagnostics: list[Diagnostic] = []
        outcome = Outcome.ERROR if undeclared_vars else Outcome.WARNING if unused_vars else Outcome.SUCCESS

        # Unused variables (provided in schema but not in template)
        for var_name in sorted(unused_vars):
            diagnostics.append(
                Diagnostic(
                    level=Outcome.WARNING,
                    message=f"Unused variable: '{var_name}'",
                    name=var_name,
                    index=self._extract_index(model_cls, var_name),
                )
            )

        # Undeclared parameters (in template but missing in schema)
        for var_name in sorted(undeclared_vars):
            diagnostics.append(
                Diagnostic(
                    level=Outcome.ERROR,
                    message=f"Undeclared variable: '{var_name}'",
                    name=var_name,
                )
            )

        if outcome is Outcome.ERROR:
            return Compilation(
                outcome=outcome,
                message="Query compilation failed",
                _spec=None,
                diagnostics=tuple(diagnostics),
            )

        return Compilation(
            outcome=outcome,
            message="Query successfully compiled with schema",
            _spec=CompilationSpec(template=template, schema=schema),
            diagnostics=tuple(diagnostics),
        )
