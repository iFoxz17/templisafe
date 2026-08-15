from templisafe.core.default_handler import DefaultHandler
from templisafe.core.outcome_handler import OutcomeHandler
from templisafe.core.util import DiagnosticPolicy
from templisafe.engine.template_engine_assembler import TemplateEngineAssembler
from templisafe.executor.source_executor_assembler import SourceExecutorAssembler
from templisafe.parser.config.config_parser_assembler import ConfigParserAssembler
from templisafe.parser.loader_facade import LoaderFacade
from templisafe.parser.schema.schema_loader import SchemaLoader
from templisafe.parser.template.template_loader import TemplateLoader
from templisafe.parser.variant.variant_loader import VariantLoader
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.source.source import Source
from templisafe.source.source_assembler import SourceAssembler
from templisafe.template.compiler.compiler_assembler import CompilerAssembler
from templisafe.template.renderer.renderer_assembler import RendererAssembler
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

        source_resolver = SourceAssembler().assemble()
        source_executor_resolver = SourceExecutorAssembler().assemble(
            default_executor_settings=source_executor_settings
        )
        config_parser_resolver = ConfigParserAssembler().assemble()

        template_engine_settings = template_engine_settings or TemplateEngineSettings.create()
        compiler_settings = compiler_settings or CompilerSettings.create()
        renderer_settings = renderer_settings or RendererSettings.create()

        loader_facade = LoaderFacade(
            template_loader=TemplateLoader(template_parser_settings),
            schema_loader=SchemaLoader(schema_parser_settings),
            variant_loader=VariantLoader(variant_parser_settings),
        )

        return Templater(
            source_resolver=source_resolver,
            source_executor_resolver=source_executor_resolver,
            config_parser_resolver=config_parser_resolver,
            template_engine_resolver=TemplateEngineAssembler().assemble(
                default_template_engine_settings=template_engine_settings
            ),
            loader_facade=loader_facade,
            compiler_resolver=CompilerAssembler().assemble(default_compiler_settings=compiler_settings),
            renderer_resolver=RendererAssembler().assemble(default_renderer_settings=renderer_settings),
            default_handler=DefaultHandler(
                template_engine_default_settings=template_engine_settings,
                compiler_default_settings=compiler_settings,
                renderer_default_settings=renderer_settings,
            ),
            outcome_handler=OutcomeHandler(policy=self._normalize_policy(diagnostic_policy)),
        )


__all__ = ["TemplaterFactory"]
