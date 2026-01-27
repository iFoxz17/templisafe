from typing import Any
from pydantic import BaseModel, ValidationError

from templisafe.engine.template_engine import TemplateEngine
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.template_model import (
    CompilationSpec,
    Schema,
    VariantSet,
    Parameterization,
    RenderingSpec,
    Outcome,
    Diagnostic,
    Rendering
)

class Renderer:
    """Renders compiled templates using a template engine."""

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self, settings: RendererSettings) -> None:
        self._settings: RendererSettings = settings

    def _extract_index(self, model_type: type[BaseModel], var_name: str) -> int | None:
        field = model_type.model_fields[var_name]
        json_dict = field.json_schema_extra
        index_value = json_dict.get(self._settings.index_key) if isinstance(json_dict, dict) else None
        index: int | None = index_value if isinstance(index_value, int) else None
        return index

    def _diagnostic_message(self, variant_name: str, msg: str) -> str:
        return f"Variant '{variant_name}' - {msg}"

    def validate(
        self,
        compiled: CompilationSpec,
        variants_set: VariantSet,
    ) -> Rendering:
        """Validate multiple variants against the compiled query schema."""

        all_diagnostics: list[Diagnostic] = []
        overall_outcome: Outcome = Outcome.SUCCESS

        schema: Schema = compiled.schema
        model_cls: type[BaseModel] = schema.model_cls
        var_names: set[str] = set(model_cls.model_fields.keys())

        for variant in variants_set.variants:
            variant_name: str = variant.name
            bindings_names: set[str] = variant.names

            diagnostics: list[Diagnostic] = []

            # Extra bindings (provided but not in schema)
            extra_bindings: set[str] = bindings_names - var_names
            for b_name in sorted(extra_bindings):
                diagnostics.append(
                    Diagnostic(
                        level=Outcome.WARNING,
                        message=self._diagnostic_message(
                            variant_name, f"Extra binding provided: '{b_name}'"
                        ),
                        name=b_name,
                        index=variant[b_name].index,
                    )
                )

            # Missing bindings (required but not provided)
            missing_bindings: set[str] = {
                name
                for name in var_names - bindings_names
                if model_cls.model_fields[name].is_required()
            }
            for b_name in sorted(missing_bindings):
                diagnostics.append(
                    Diagnostic(
                        level=Outcome.ERROR,
                        message=self._diagnostic_message(
                            variant_name, f"Missing required binding: '{b_name}'"
                        ),
                        name=b_name,
                        index=self._extract_index(model_cls, b_name)
                    )
                )

            # Wrong typed bindings
            bindings: set[str] = bindings_names & var_names
            try:
                model_cls(**{b.name: b.value for b in variant if b.name in bindings})
            except ValidationError as e:
                for err in e.errors():
                    name: str = str(err["loc"][0])
                    diagnostics.append(
                        Diagnostic(
                            level=Outcome.ERROR,
                            message=self._diagnostic_message(
                                variant_name,
                                f"Invalid value for binding '{name}': {err['msg']}"
                            ),
                            name=name,
                            index=variant[name].index if name in variant else None,
                        )
                    )

            # Determine outcome for this variant
            outcome: Outcome = (
                Outcome.ERROR
                if any(d.level == Outcome.ERROR for d in diagnostics)
                else Outcome.WARNING
                if diagnostics
                else Outcome.SUCCESS
            )
            if outcome > overall_outcome:
                overall_outcome = outcome

            all_diagnostics.extend(diagnostics)

        message = (
            "Validation successful"
            if overall_outcome == Outcome.SUCCESS
            else "Validation completed with warnings"
            if overall_outcome == Outcome.WARNING
            else "Validation failed due to errors"
        )

        return Rendering(
            outcome=overall_outcome,
            message=message,
            _spec=None,
            diagnostics=tuple(all_diagnostics),
        )

    def render(
        self,
        compiled: CompilationSpec,
        variants_set: VariantSet,
        engine: TemplateEngine,
    ) -> Rendering:
        """Render multiple variants against the compiled query schema."""
        
        validation: Rendering = self.validate(compiled, variants_set)
        if validation.outcome == Outcome.ERROR:
            return validation  # Do not render if validation failed

        parameterizations: list[Parameterization] = []

        model_cls = compiled.schema.model_cls
        var_names: set[str] = set(model_cls.model_fields.keys())

        for variant in variants_set.variants:
            binding_value_map: dict[str, Any] = {bn: b.value for bn, b in variant.mapping.items()}

            # Fill in default values for missing fields
            for var_name in var_names - variant.names:
                field = model_cls.model_fields[var_name]
                assert field.default is not None
                binding_value_map[var_name] = field.default

            # Render template
            rendered_str: str = engine.render(compiled.template.template_str, binding_value_map)
            param = Parameterization(variant=variant, rendered_str=rendered_str)
            parameterizations.append(param)

        rendered_query = RenderingSpec(parameterizations)
        message = (
            "Rendering successful"
            if validation.outcome == Outcome.SUCCESS
            else "Rendering completed with warnings"
        )

        return Rendering(
            outcome=validation.outcome,
            message=message,
            _spec=rendered_query,
            diagnostics=validation.diagnostics,
        )