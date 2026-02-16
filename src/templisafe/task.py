from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from enum import Enum, auto
from typing import Any

import attr
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
    template_engine : TemplateEngine | TemplateEngineSettings | Source | SourceSettings | None
        The engine or engine settings to use for template processing.
    source_executor_settings : Source | SourceSettings | SourceExecutorSettings | None
        Settings or source to execute external sources.
    """
    template_engine: TemplateEngine | TemplateEngineSettings | Source | SourceSettings | None = None
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
    template : str | Source | SourceSettings
        The template or source for the compilation.
    schema : Config | Source | SourceSettings | None
        The schema or source for schema input.
    template_parser_settings : Source | SourceSettings | TemplateParserSettings | None
        Optional template parser configuration.
    schema_parser_settings : Source | SourceSettings | SchemaParserSettings | None
        Optional schema parser configuration.
    compiler_settings : Source | SourceSettings | CompilerSettings | None
        Optional compiler settings.
    """
    template: str | Source | SourceSettings
    schema: Config | Source | SourceSettings | None = None
    template_parser_settings: Source | SourceSettings | TemplateParserSettings | None = None
    schema_parser_settings: Source | SourceSettings | SchemaParserSettings | None = None
    compiler_settings: Source | SourceSettings | CompilerSettings | None = None

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
    variants : Config | Source | SourceSettings | list[Source | SourceSettings]
        Variant definitions or sources.
    variant_parser_settings : Source | SourceSettings | SchemaParserSettings | None
        Optional parser settings for variants.
    renderer_settings : Source | SourceSettings | SchemaParserSettings | None
        Optional renderer settings.
    """
    compiled: CompilationSpec
    variants: Config | Source | SourceSettings | list[Source | SourceSettings]
    variant_parser_settings: Source | SourceSettings | SchemaParserSettings | None = None
    renderer_settings: Source | SourceSettings | SchemaParserSettings | None = None

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
    template : str | Source | SourceSettings
        Template or source.
    variants : Config | Source | SourceSettings | list[Source | SourceSettings]
        Variant definitions or sources.
    schema : Config | Source | SourceSettings | None
        Schema for the build.
    template_parser_settings : Source | SourceSettings | TemplateParserSettings | None
        Optional template parser settings.
    schema_parser_settings : Source | SourceSettings | SchemaParserSettings | None
        Optional schema parser settings.
    variant_parser_settings : Source | SourceSettings | SchemaParserSettings | None
        Optional variant parser settings.
    compiler_settings : Source | SourceSettings | CompilerSettings | None
        Optional compiler settings.
    renderer_settings : Source | SourceSettings | SchemaParserSettings | None
        Optional renderer settings.
    """
    template: str | Source | SourceSettings
    variants: Config | Source | SourceSettings | list[Source | SourceSettings]
    schema: Config | Source | SourceSettings | None = None
    template_parser_settings: Source | SourceSettings | TemplateParserSettings | None = None
    schema_parser_settings: Source | SourceSettings | SchemaParserSettings | None = None
    variant_parser_settings: Source | SourceSettings | SchemaParserSettings | None = None
    compiler_settings: Source | SourceSettings | CompilerSettings | None = None
    renderer_settings: Source | SourceSettings | SchemaParserSettings | None = None

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
