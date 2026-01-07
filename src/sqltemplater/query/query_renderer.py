from typing import Any
from jinja2 import Environment, Template

from sqltemplater.query.query_model import (
    QCompilationSpec,
    QVar,
    QBinding,
    QSchema,
    QVariant,
    QVariantSet,
    QParameterization,
    QRenderingSpec,
    QOutcome,
    QDiagnostic,
    QRendering
)

class QueryRenderer:
    """Renders compiled queries using Jinja2 Environment, with diagnostics."""

    __slots__: tuple[str, ...] = ("_env",)

    def __init__(self, env: Environment) -> None:
        self._env: Environment = env

    def _diagnostic_message(self, variant_name: str, msg: str) -> str:
        return f"'{variant_name}' - {msg}"

    def validate(
        self,
        compiled: QCompilationSpec,
        variants_set: QVariantSet
    ) -> QRendering:
        """Validate multiple variants against the compiled query schema."""
        all_diagnostics: list[QDiagnostic] = []
        overall_outcome: QOutcome = QOutcome.SUCCESS

        schema: QSchema = compiled.schema
        var_names: set[str] = schema.names
            
        for variant in variants_set.variants:
            variant_name: str = variant.name
            bindings_names: set[str] = variant.names

            diagnostics: list[QDiagnostic] = []

            # Extra bindings (provided but not in schema)
            extra_bindings: set[str] = bindings_names - var_names
            for b_name in sorted(extra_bindings):
                diagnostics.append(QDiagnostic(
                    level=QOutcome.WARNING,
                    message=self._diagnostic_message(
                        variant_name, 
                        f"Extra binding provided: '{b_name}'"
                        ),
                    name=b_name,
                    index=None
                ))

            # Missing bindings (required but not provided)
            missing_bindings: set[str] = {name for name in var_names - bindings_names if not schema[name].has_default}
            for b_name in sorted(missing_bindings):
                diagnostics.append(QDiagnostic(
                    level=QOutcome.ERROR,
                    message=self._diagnostic_message(
                        variant_name, 
                        f"Missing required binding: '{b_name}'"
                        ),
                    name=b_name,
                    index=schema[b_name].index
                ))

            # Wrong typed bindings
            bindings: set[str] = bindings_names & var_names
            for b_name in sorted(bindings):
                binding: QBinding = variant[b_name]
                var: QVar = schema[b_name]
                if not isinstance(binding.value, var.type_):
                    diagnostics.append(QDiagnostic(
                        level=QOutcome.ERROR,
                        message=self._diagnostic_message(
                        variant_name, 
                        f"Wrong type for binding '{b_name}': expecting '{var.type_.__name__}', got '{type(binding.value)}'"
                        ),
                        name=b_name,
                        index=binding.index
                    ))

            # Determine outcome for this rendering
            outcome: QOutcome = (
                QOutcome.ERROR if any(d.level == QOutcome.ERROR for d in diagnostics)
                else QOutcome.WARNING if diagnostics else QOutcome.SUCCESS
            )

            if outcome > overall_outcome:
                overall_outcome = outcome

            all_diagnostics.extend(diagnostics)

        message: str = (
            "Validation successful" if overall_outcome == QOutcome.SUCCESS
            else "Validation completed with warnings" if overall_outcome == QOutcome.WARNING
            else "Validation failed due to errors"
        )

        return QRendering(
            outcome=overall_outcome,
            message=message,
            _spec=None,
            diagnostics=tuple(all_diagnostics)
        )

    def render(
        self,
        compiled: QCompilationSpec,
        variants_set: QVariantSet,
        env: Environment | None = None
    ) -> QRendering:
        """Render the compiled query for all variants using the given or default Jinja environment."""
        env_to_use: Environment = env or self._env

        validation: QRendering = self.validate(compiled, variants_set)
        if validation.outcome == QOutcome.ERROR:
            # Do not render if validation failed
            return validation

        parameterizations: list[QParameterization] = []

        for variant in variants_set.variants:
            values_map: dict[str, Any] = {bn: b.value for bn, b in variant.mapping.items()}
            
            schema: QSchema = compiled.schema
            defaulted_var_names: set[str] = schema.names - variant.names
            for var_name in defaulted_var_names:
                assert schema[var_name].has_default
                values_map[var_name] = schema[var_name].default
            
            # Render template
            template: Template = env_to_use.from_string(compiled.template.template)
            rendered_str: str = template.render(**values_map)
            
            param: QParameterization = QParameterization(
                variant=variant,
                rendered=rendered_str
                )
            parameterizations.append(param)

        rendered_query: QRenderingSpec = QRenderingSpec(parameterizations)

        message: str = (
            "Rendering successful" if validation.outcome == QOutcome.SUCCESS
            else "Rendering completed with warnings"
        )

        return QRendering(
            outcome=validation.outcome,
            message=message,
            _spec=rendered_query,
            diagnostics=validation.diagnostics
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(_env={self._env!r})"
