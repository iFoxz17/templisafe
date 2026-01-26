from typing import Any, Union
from dataclasses import dataclass, fields

from templisafe.executor.source_executor import SourceExecutor
from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.template.template_parser import TemplateParser
from templisafe.parser.variant.variant_parser import VariantParser

from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.settings import Settings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings

from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.source.source import Source

from templisafe.engine.template_engine import TemplateEngine

from templisafe.template.compiler.compiler import Compiler
from templisafe.template.renderer.renderer import Renderer

#---------------------------------------------------------------------------------------------
# Templater input
#---------------------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TemplaterInput:
    template: SourceOrSettings
    variants: SourceOrSettings | list[SourceOrSettings]
    schema: SourceOrSettings | None = None

    template_engine: SourceOrSettings | TemplateEngineSettings | TemplateEngine | None = None
    source_executor_settings: SourceOrSettings | SourceExecutorSettings | None = None
    template_parser_settings: SourceOrSettings | TemplateParserSettings | None = None
    schema_parser_settings: SourceOrSettings | SchemaParserSettings | None = None
    variant_parser_settings: SourceOrSettings | VariantParserSettings | None = None
    compiler_settings: SourceOrSettings | CompilerSettings | None = None
    renderer_settings: SourceOrSettings | CompilerSettings | None = None