from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from enum import Enum, auto
from typing import Any

from overrides import overrides

from templisafe.engine.template_engine import TemplateEngine
from templisafe.parser.config.config_parser import Config
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.source.source import Source
from templisafe.template.template_model import CompilationSpec


class TaskType(Enum):
    """Enumeration of task types."""
    COMPILATION = auto()
    RENDERING = auto()
    BUILD = auto()

@dataclass(frozen=True, slots=True, kw_only=True)
class TaskBundle(ABC):
    """
    Base class for all task bundles.

    Attributes
    ----------
    template_engine : SourceSettings | Source | TemplateEngineSettings | TemplateEngine | None
        The engine or engine settings to use for template processing.
    source_executor_settings : Source | SourceSettings | SourceExecutorSettings | None
        Settings or source to execute external sources.
    """
    template_engine: SourceSettings | Source | TemplateEngineSettings | TemplateEngine | None = None
    source_executor_settings: SourceExecutorSettings | None = None

    @property
    @abstractmethod
    def type_(self) -> TaskType:
        """Return the type of task represented by this bundle."""
        pass


@dataclass(frozen=True, slots=True)
class CompilationBundle(TaskBundle):
    """
    Bundle representing a compilation task.

    Attributes
    ----------
    template: SourceSettings | Source | str
        The template or source for the compilation.
    schema : SourceSettings | Source | Config | None
        The schema or source for schema input.
    template_parser_settings : SourceSettings | Source | TemplateParserSettings | Config | None
        Optional template parser configuration.
    schema_parser_settings : SourceSettings | Source | SchemaParserSettings | Config | None
        Optional schema parser configuration.
    compiler_settings : SourceSettings | Source | CompilerSettings | Config | None
        Optional compiler settings.
    """
    template: SourceSettings | Source | str
    schema: SourceSettings | Source | Config | None = None
    template_parser_settings: SourceSettings | Source | TemplateParserSettings | Config | None = None
    schema_parser_settings: SourceSettings | Source | SchemaParserSettings | Config | None = None
    compiler_settings: SourceSettings | Source | CompilerSettings | Config | None = None

    @property
    @overrides
    def type_(self) -> TaskType:
        return TaskType.COMPILATION


@dataclass(frozen=True, slots=True)
class RenderingBundle(TaskBundle):
    """
    Bundle representing a rendering task.

    Attributes
    ----------
    compiled : CompilationSpec
        Compiled template specification.
    variants : SourceSettings | Source | list[Source | SourceSettings] | Config
        Variant definitions or sources.
    variant_parser_settings : SourceSettings | Source | SchemaParserSettings | Config | None
        Optional parser settings for variants.
    renderer_settings : SourceSettings | Source | SchemaParserSettings | Config | None
        Optional renderer settings.
    """
    compiled: CompilationSpec
    variants: SourceSettings | Source | list[Source | SourceSettings] | Config
    variant_parser_settings: SourceSettings | Source | SchemaParserSettings | Config | None = None
    renderer_settings: SourceSettings | Source | SchemaParserSettings | Config | None = None

    @property
    @overrides
    def type_(self) -> TaskType:
        return TaskType.RENDERING


@dataclass(frozen=True, slots=True)
class BuildBundle(TaskBundle):
    """
    Bundle representing a build task combining compilation and rendering.

    Attributes
    ----------
    template : SourceSettings | Source | str
        Template or source.
    variants : SourceSettings | Source | list[Source | SourceSettings] | Config
        Variant definitions or sources.
    schema : SourceSettings | Source | Config | None
        Schema for the build.
    template_parser_settings : SourceSettings | Source | TemplateParserSettings | Config | None
        Optional template parser settings.
    schema_parser_settings : SourceSettings | Source | SchemaParserSettings | Config | None
        Optional schema parser settings.
    variant_parser_settings : SourceSettings | Source | SchemaParserSettings | Config | None
        Optional variant parser settings.
    compiler_settings : SourceSettings | Source | CompilerSettings | Config | None
        Optional compiler settings.
    renderer_settings : SourceSettings | Source | SchemaParserSettings | Config | None
        Optional renderer settings.
    """
    template: SourceSettings | Source | str
    variants: SourceSettings | Source | list[Source | SourceSettings] | Config
    schema: SourceSettings | Source | Config | None = None
    template_parser_settings: SourceSettings | Source | TemplateParserSettings | Config | None = None
    schema_parser_settings: SourceSettings | Source | SchemaParserSettings | Config | None = None
    variant_parser_settings: SourceSettings | Source | SchemaParserSettings | Config | None = None
    compiler_settings: SourceSettings | Source | CompilerSettings | Config | None = None
    renderer_settings: SourceSettings | Source | SchemaParserSettings | Config | None = None

    @property
    @overrides
    def type_(self) -> TaskType:
        return TaskType.BUILD


@dataclass(frozen=True, slots=True)
class Task:
    """
    Represents a task to execute with its corresponding bundle.

    Attributes
    ----------
    bundle : TaskBundle
        The bundle containing all necessary data to execute the task.
    """
    bundle: TaskBundle

    @property
    def type_(self) -> TaskType:
        """Infer the task type from the bundle."""
        return self.bundle.type_
