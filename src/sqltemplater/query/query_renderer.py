from typing import Any
from jinja2 import Environment, Template

from sqltemplater.query.query_model import (
    CompiledQuery,
    ParamSchema,
    QuerySchema,
    QueryParams,
    QueryParameterization,
    RenderedQuery,
    BuildOutcome,
    BuildDiagnostic,
    RenderingResult
)

class QueryRenderer:
    """Renders compiled queries using Jinja2 Environment, with diagnostics."""

    __slots__ = ("_env",)

    def __init__(self, env: Environment) -> None:
        self._env: Environment = env

    def validate(
        self,
        compiled: CompiledQuery,
        parameterizations: QueryParameterization
    ) -> RenderingResult:
        """Validate multiple parameterizations against the compiled query schema."""
        all_diagnostics: list[BuildDiagnostic] = []
        overall_outcome: BuildOutcome = BuildOutcome.SUCCESS

        schema: QuerySchema = compiled.schema
        schema_names: set[str] = schema.names
            
        for params_name, params in parameterizations.parameterizations.items():
            param_names: set[str] = {p.name for p in params.params}

            diagnostics: list[BuildDiagnostic] = []

            # Extra parameters (provided but not in schema)
            extra_params: set[str] = param_names - schema_names
            for name in sorted(extra_params):
                diagnostics.append(BuildDiagnostic(
                    level=BuildOutcome.WARNING,
                    message=f"Extra parameter provided: '{name}'",
                    param=name,
                    index=None
                ))

            # Missing parameters (required but not provided)
            missing_params: set[str] = {name for name in schema_names - param_names if not schema[name].has_default}
            for name in sorted(missing_params):
                diagnostics.append(BuildDiagnostic(
                    level=BuildOutcome.ERROR,
                    message=f"Missing required parameter: '{name}'",
                    param=name,
                    index=schema[name].index
                ))

            # Determine outcome for this parameterization
            outcome: BuildOutcome = (
                BuildOutcome.ERROR if any(d.level == BuildOutcome.ERROR for d in diagnostics)
                else BuildOutcome.WARNING if diagnostics else BuildOutcome.SUCCESS
            )

            if outcome > overall_outcome:
                overall_outcome = outcome

            all_diagnostics.extend(diagnostics)

        message: str = (
            "Validation successful" if overall_outcome == BuildOutcome.SUCCESS
            else "Validation completed with warnings" if overall_outcome == BuildOutcome.WARNING
            else "Validation failed due to errors"
        )

        return RenderingResult(
            outcome=overall_outcome,
            message=message,
            rendered_query=None
        )

    def render(
        self,
        compiled: CompiledQuery,
        parameterizations: QueryParameterization,
        env: Environment | None = None
    ) -> RenderingResult:
        """Render the compiled query for all parameterizations using the given or default Jinja environment."""
        env_to_use: Environment = env or self._env

        validation_result: RenderingResult = self.validate(compiled, parameterizations)
        if validation_result.outcome == BuildOutcome.ERROR:
            # Do not render if validation failed
            return validation_result

        rendered_list: list[str] = []
        all_diagnostics: list[BuildDiagnostic] = []

        for _, params in parameterizations.parameterizations.items():
            # Build param map including defaults
            param_map: dict[str, Any] = params.params_map.copy()
            for s in compiled.schema.params:
                if s.name not in param_map and s.has_default:
                    param_map[s.name] = s.default

            # Render template
            template: Template = env_to_use.from_string(compiled.template.template)
            rendered_str: str = template.render(**param_map)
            rendered_list.append(rendered_str)

        rendered_query: RenderedQuery = RenderedQuery(
            compiled=compiled,
            parameterization=parameterizations,
            rendered=rendered_list,
            diagnostics=tuple(all_diagnostics)
        )

        message: str = (
            "Rendering successful" if validation_result.outcome == BuildOutcome.SUCCESS
            else "Rendering completed with warnings"
        )

        return RenderingResult(
            outcome=validation_result.outcome,
            message=message,
            rendered_query=rendered_query
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(_env={self._env!r})"
