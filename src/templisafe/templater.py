from typing import TypeAlias

from templisafe.engine.template_engine import TemplateEngine
from templisafe.handler.outcome_handler import OutcomeHandler
from templisafe.input import SchemaInput, TemplateInput, VariantInput, VariantSetInput
from templisafe.parser.config.config_parser import Config
from templisafe.service.service_orchestrator import ServiceOrchestrator
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.source.source import Source
from templisafe.task.task import BuildBundle, CompilationBundle, RenderingBundle, Task
from templisafe.task.task_validator import TaskValidator
from templisafe.template.template_model import (
    Build,
    Compilation,
    CompilationSpec,
    Rendering,
)

SourceLike: TypeAlias = Source | SourceSettings
ConfigLike: TypeAlias = SourceLike | Config
TemplateLike: TypeAlias = SourceLike | str | TemplateInput
SchemaLike: TypeAlias = ConfigLike | SchemaInput
VariantsLike: TypeAlias = (
    ConfigLike | VariantInput | VariantSetInput | list[ConfigLike | VariantInput | VariantSetInput]
)
SettingsLike: TypeAlias = SourceLike


class Templater:
    """
    Public orchestrator for template workflows.

    `Templater` is the API boundary: it creates task objects, validates them,
    delegates execution to the service orchestrator and applies outcome policy.
    """

    __slots__: tuple[str, ...] = (
        "_task_validator",
        "_service_orchestrator",
        "_outcome_handler",
    )

    def __init__(
        self,
        *,
        task_validator: TaskValidator,
        service_orchestrator: ServiceOrchestrator,
        outcome_handler: OutcomeHandler,
    ) -> None:
        self._task_validator = task_validator
        self._service_orchestrator = service_orchestrator
        self._outcome_handler = outcome_handler

    def _execute(self, task: Task) -> Compilation | Rendering | Build:
        self._task_validator.validate(task)
        return self._service_orchestrator.process(task)

    def compile(
        self,
        template: TemplateLike,
        schema: SchemaLike | None = None,
        *,
        template_engine: (TemplateEngine | TemplateEngineSettings | SettingsLike | None) = None,
        source_executor_settings: SourceExecutorSettings | SettingsLike | None = None,
        template_parser_settings: TemplateParserSettings | SettingsLike | None = None,
        schema_parser_settings: SchemaParserSettings | SettingsLike | None = None,
        compiler_settings: CompilerSettings | SettingsLike | None = None,
    ) -> Compilation:
        task = Task(
            bundle=CompilationBundle(
                template=template,
                schema_=schema,
                template_engine=template_engine,
                source_executor_settings=source_executor_settings,
                template_parser_settings=template_parser_settings,
                schema_parser_settings=schema_parser_settings,
                compiler_settings=compiler_settings,
            )
        )
        result = self._execute(task)
        if not isinstance(result, Compilation):
            raise TypeError("Compilation task did not return Compilation")
        self._outcome_handler.handle_compilation(result)
        return result

    def render(
        self,
        compiled: CompilationSpec,
        variants: VariantsLike,
        *,
        template_engine: (TemplateEngine | TemplateEngineSettings | SettingsLike | None) = None,
        source_executor_settings: SourceExecutorSettings | SettingsLike | None = None,
        variant_parser_settings: VariantParserSettings | SettingsLike | None = None,
        renderer_settings: RendererSettings | SettingsLike | None = None,
    ) -> Rendering:
        task = Task(
            bundle=RenderingBundle(
                compiled=compiled,
                variants=variants,
                render=True,
                template_engine=template_engine,
                source_executor_settings=source_executor_settings,
                variant_parser_settings=variant_parser_settings,
                renderer_settings=renderer_settings,
            )
        )
        result = self._execute(task)
        if not isinstance(result, Rendering):
            raise TypeError("Rendering task did not return Rendering")
        self._outcome_handler.handle_rendering(result)
        return result

    def validate(
        self,
        compiled: CompilationSpec,
        variants: VariantsLike,
        *,
        source_executor_settings: SourceExecutorSettings | SettingsLike | None = None,
        variant_parser_settings: VariantParserSettings | SettingsLike | None = None,
        renderer_settings: RendererSettings | SettingsLike | None = None,
    ) -> Rendering:
        task = Task(
            bundle=RenderingBundle(
                compiled=compiled,
                variants=variants,
                render=False,
                source_executor_settings=source_executor_settings,
                variant_parser_settings=variant_parser_settings,
                renderer_settings=renderer_settings,
            )
        )
        result = self._execute(task)
        if not isinstance(result, Rendering):
            raise TypeError("Validation task did not return Rendering")
        self._outcome_handler.handle_validation(result)
        return result

    def build(
        self,
        template: TemplateLike,
        variants: VariantsLike,
        schema: SchemaLike | None = None,
        *,
        template_engine: (TemplateEngine | TemplateEngineSettings | SettingsLike | None) = None,
        source_executor_settings: SourceExecutorSettings | SettingsLike | None = None,
        template_parser_settings: TemplateParserSettings | SettingsLike | None = None,
        schema_parser_settings: SchemaParserSettings | SettingsLike | None = None,
        variant_parser_settings: VariantParserSettings | SettingsLike | None = None,
        compiler_settings: CompilerSettings | SettingsLike | None = None,
        renderer_settings: RendererSettings | SettingsLike | None = None,
    ) -> Build:
        task = Task(
            bundle=BuildBundle(
                template=template,
                variants=variants,
                schema_=schema,
                template_engine=template_engine,
                source_executor_settings=source_executor_settings,
                template_parser_settings=template_parser_settings,
                schema_parser_settings=schema_parser_settings,
                variant_parser_settings=variant_parser_settings,
                compiler_settings=compiler_settings,
                renderer_settings=renderer_settings,
            )
        )
        result = self._execute(task)
        if not isinstance(result, Build):
            raise TypeError("Build task did not return Build")
        self._outcome_handler.handle_compilation(result.compilation)
        self._outcome_handler.handle_rendering(result.rendering)
        return result
