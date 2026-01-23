from dataclasses import dataclass, fields
from typing import Any

from templisafe.templater_model import TemplaterInput
from templisafe.executor.source_executor import SourceExecutorResult
from templisafe.settings.settings import Settings

from templisafe.settings.settings import Settings
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings

#---------------------------------------------------------------------------------------------
# Settings resolution
#---------------------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ResolvedSettings:
    template_engine_settings: TemplateEngineSettings | None = None
    template_parser_settings: TemplateParserSettings | None = None
    schema_parser_settings: SchemaParserSettings | None = None
    variant_parser_settings: VariantParserSettings | None = None
    compiler_settings: CompilerSettings | None = None
    renderer_settings: RendererSettings | None = None

    @property
    def resolved(self) -> dict[str, Settings]:
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if getattr(self, f.name) is not None
        }


#---------------------------------------------------------------------------------------------
# Resolver
#---------------------------------------------------------------------------------------------

class SettingsResolver:
    """
    Resolve effective settings by merging user-provided settings from the input
    with settings produced by the SourceExecutor.

    Explicit settings provided by the user always take precedence.
    """

    __slots__ = ()

    def resolve(
        self,
        input: TemplaterInput,
        executor_result: SourceExecutorResult,
    ) -> ResolvedSettings:
        def pick(
            user_value: object,
            resolved_value: Settings | None,
            expected_type: type[Settings],
        ) -> Any:
            return (
                user_value
                if isinstance(user_value, expected_type)
                else resolved_value
            )

        return ResolvedSettings(
            template_engine_settings=pick(
                input.template_engine,
                executor_result.template_engine_settings,
                TemplateEngineSettings,
            ),
            template_parser_settings=pick(
                input.template_parser_settings,
                executor_result.template_parser_settings,
                TemplateParserSettings,
            ),
            schema_parser_settings=pick(
                input.schema_parser_settings,
                executor_result.schema_parser_settings,
                SchemaParserSettings,
            ),
            variant_parser_settings=pick(
                input.variant_parser_settings,
                executor_result.variant_parser_settings,
                VariantParserSettings,
            ),
            compiler_settings=pick(
                input.compiler_settings,
                executor_result.compiler_settings,
                CompilerSettings,
            ),
            renderer_settings=pick(
                input.renderer_settings,
                executor_result.renderer_settings,
                RendererSettings,
            ),
        )
