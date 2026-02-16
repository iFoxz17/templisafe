from dataclasses import make_dataclass, field, fields
from typing import Any, get_type_hints

from templisafe.content.content import Content, ContentType
from templisafe.parser.config.config_parser import Config, ConfigParser
from templisafe.provider.config_parser_provider import ConfigParserProvider
from templisafe.service.field_selector import FieldSelector
from templisafe.task import TaskBundle

class ConfigService:
    """Service responsible for resolving Config fields from a DataBundle."""

    __slots__ = ("_config_parser_provider", "_field_selector")

    def __init__(self, config_parser_provider: ConfigParserProvider, field_selector: FieldSelector) -> None:
        self._config_parser_provider: ConfigParserProvider = config_parser_provider
        self._field_selector: FieldSelector = field_selector

    def process(self, data_bundle: TaskBundle) -> TaskBundle:
        """
        Process a DataBundle with all fields at least at the Content level
        and produce a ConfigBundle with resolved Config fields.
        """

        # Prepare a parser cache per ContentType
        content_fields: dict[str, Content] = self._field_selector.select_by_type(data_bundle, Content)
        config_fields: dict[str, Config] = {}
        
        for name, content in content_fields.items():
            content_type: ContentType = content.type_
            parser: ConfigParser = self._config_parser_provider.provide(content_type) 
            config_fields[name] = parser.parse(content.payload)

        # Get type hints from the input bundle for any non-Content fields
        type_hints: dict[str, Any] = get_type_hints(type(data_bundle))

        # Dynamically create the ConfigBundle dataclass
        fs: list[tuple[str, type, Any]] = []
        for f in fields(data_bundle):
            if f.name in config_fields:
                # Use a default parameter to capture the current value of config_fields[f.name]
                # This avoids the common “late binding” problem in Python loops, ensuring each
                # field’s default_factory returns the correct Config at dataclass instantiation.
                fs.append((f.name, object, field(default_factory=lambda c=config_fields[f.name]: c)))
            else:
                # Keep original type and value (pass-through)
                field_type: type = type_hints.get(f.name, f.type)
                fs.append((f.name, field_type, field(default=getattr(data_bundle, f.name))))

        ConfigBundle: type[TaskBundle] = make_dataclass(
            cls_name="ConfigBundle",
            fields=fs,
            bases=(type(data_bundle),),
            frozen=True,
            slots=True,
            kw_only=True,
        )

        return ConfigBundle()