from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Annotated,
    Any,
    ClassVar,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    Type,
    TypeVar,
    ValuesView,
)

from pydantic import BaseModel, ConfigDict, Field

from templisafe.core.metadata import Metadata, MetaValue
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

# ============================================================
# Task Type
# ============================================================


class TaskType(Enum):
    COMPILATION = auto()
    RENDERING = auto()
    BUILD = auto()


# ============================================================
# Field Category
# ============================================================


class FieldCategory(Enum):
    RESOURCE = auto()
    COMPONENT = auto()


FIELD_CATEGORY_KEY: str = "category"


def CategoryMetadata(category: FieldCategory) -> Metadata:
    """Create a Metadata object storing the category for a field."""
    return Metadata({FIELD_CATEGORY_KEY: MetaValue(value=category, description="Bundle field category")})


# ============================================================
# Base Bundle
# ============================================================


class TaskBundle(BaseModel, ABC):
    """Base class for all task bundles."""

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
    )

    _type: ClassVar[TaskType]

    template_engine: Annotated[
        SourceSettings | Source | TemplateEngineSettings | TemplateEngine | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None

    source_executor_settings: Annotated[
        SourceExecutorSettings | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None

    # --------------------------------------------------------

    def _by_category(self, category: FieldCategory) -> dict[str, Any]:
        """Return a dict of field names to values filtered by category metadata."""
        result = {}
        cls = type(self)
        for name, field_info in cls.model_fields.items():
            metadata: Iterable = getattr(field_info, "metadata", ())
            for meta in metadata:
                if isinstance(meta, Metadata):
                    cat = meta.get(FIELD_CATEGORY_KEY)
                    if isinstance(cat, MetaValue) and cat.value is category:
                        result[name] = getattr(self, name)
        return result

    # --------------------------------------------------------

    @property
    def type(self) -> TaskType:
        return self._type

    @property
    def resources(self) -> dict[str, Any]:
        return self._by_category(FieldCategory.RESOURCE)

    @property
    def components(self) -> dict[str, Any]:
        return self._by_category(FieldCategory.COMPONENT)


# ============================================================
# Compilation Bundle
# ============================================================


class CompilationBundle(TaskBundle):
    _type: ClassVar[TaskType] = TaskType.COMPILATION

    template: Annotated[
        SourceSettings | Source | str,
        Field(default=...),
        CategoryMetadata(FieldCategory.RESOURCE),
    ]

    schema_: Annotated[
        SourceSettings | Source | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.RESOURCE),
    ] = None

    template_parser_settings: Annotated[
        SourceSettings | Source | TemplateParserSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None

    schema_parser_settings: Annotated[
        SourceSettings | Source | SchemaParserSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None

    compiler_settings: Annotated[
        SourceSettings | Source | CompilerSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None


# ============================================================
# Rendering Bundle
# ============================================================


class RenderingBundle(TaskBundle):
    _type: ClassVar[TaskType] = TaskType.RENDERING

    compiled: Annotated[CompilationSpec, Field(default=...), CategoryMetadata(FieldCategory.RESOURCE)]

    variants: Annotated[
        SourceSettings | Source | list[Source | SourceSettings] | Config,
        Field(default=...),
        CategoryMetadata(FieldCategory.RESOURCE),
    ]

    variant_parser_settings: Annotated[
        SourceSettings | Source | SchemaParserSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None

    renderer_settings: Annotated[
        SourceSettings | Source | SchemaParserSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None


# ============================================================
# Build Bundle
# ============================================================


class BuildBundle(TaskBundle):
    _type: ClassVar[TaskType] = TaskType.BUILD

    template: Annotated[
        SourceSettings | Source | str,
        Field(default=...),
        CategoryMetadata(FieldCategory.RESOURCE),
    ]

    variants: Annotated[
        SourceSettings | Source | list[Source | SourceSettings] | Config,
        Field(default=...),
        CategoryMetadata(FieldCategory.RESOURCE),
    ]

    schema_: Annotated[
        SourceSettings | Source | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.RESOURCE),
    ] = None

    template_parser_settings: Annotated[
        SourceSettings | Source | TemplateParserSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None

    schema_parser_settings: Annotated[
        SourceSettings | Source | SchemaParserSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None

    variant_parser_settings: Annotated[
        SourceSettings | Source | SchemaParserSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None

    compiler_settings: Annotated[
        SourceSettings | Source | CompilerSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None

    renderer_settings: Annotated[
        SourceSettings | Source | SchemaParserSettings | Config | None,
        Field(default=None),
        CategoryMetadata(FieldCategory.COMPONENT),
    ] = None


# ============================================================
# Task Wrapper
# ============================================================


class Task(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
    )

    bundle: TaskBundle

    @property
    def type(self) -> TaskType:
        return self.bundle.type
