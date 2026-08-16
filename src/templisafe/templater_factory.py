from templisafe.core.util import DiagnosticPolicy
from templisafe.handler.outcome_handler import OutcomeHandler
from templisafe.service.service_assembler import ServiceAssembler
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.task.task_validator import TaskValidator
from templisafe.templater import Templater


class TemplaterFactory:
    """
    Factory for creating ready-to-use `Templater` instances.

    Defaults target the first operative version: inline/local sources, YAML/JSON/TOML/XML
    configuration parsing, Jinja templates, Pydantic schema validation and multi-variant
    rendering.
    """

    def _normalize_policy(
        self,
        diagnostic_policy: DiagnosticPolicy | str | None,
    ) -> DiagnosticPolicy:
        if diagnostic_policy is None:
            return DiagnosticPolicy.LOG
        if isinstance(diagnostic_policy, DiagnosticPolicy):
            return diagnostic_policy
        try:
            return DiagnosticPolicy(diagnostic_policy)
        except ValueError as e:
            raise ValueError(f"Invalid diagnostic policy provided: {diagnostic_policy}") from e

    def create(
        self,
        *,
        source_executor_settings: SourceExecutorSettings | None = None,
        template_engine_settings: TemplateEngineSettings | None = None,
        template_parser_settings: TemplateParserSettings | None = None,
        schema_parser_settings: SchemaParserSettings | None = None,
        variant_parser_settings: VariantParserSettings | None = None,
        compiler_settings: CompilerSettings | None = None,
        renderer_settings: RendererSettings | None = None,
        diagnostic_policy: DiagnosticPolicy | str | None = None,
    ) -> Templater:
        """
        Create a fully configured `Templater`.

        Factory-level settings must be concrete settings instances. Per-call public
        methods also accept settings from sources when that is more convenient.
        """

        return Templater(
            task_validator=TaskValidator(),
            service_orchestrator=ServiceAssembler().assemble(
                source_executor_settings=source_executor_settings,
                template_engine_settings=template_engine_settings,
                template_parser_settings=template_parser_settings,
                schema_parser_settings=schema_parser_settings,
                variant_parser_settings=variant_parser_settings,
                compiler_settings=compiler_settings,
                renderer_settings=renderer_settings,
            ),
            outcome_handler=OutcomeHandler(policy=self._normalize_policy(diagnostic_policy)),
        )


__all__ = ["TemplaterFactory"]
