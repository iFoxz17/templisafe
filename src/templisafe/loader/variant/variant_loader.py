from overrides import overrides
from typing import Any

from templisafe.template.template_model import VariantSet
from templisafe.loader.variant.variant_parser import VariantParser
from templisafe.source.source import Source
from templisafe.source.inline_source import InlineSource
from templisafe.settings.source_settings import InlineSourceSettings
from templisafe.loader.variant.variant_parser_manager import VariantParserManager
from templisafe.loader.loader import Loader, LoaderContext
from templisafe.settings.parser.parser_settings import ParserSettings
from templisafe.settings.parser.variant_parser_settings import YamlVariantParserSettings, VariantParserSettings
from templisafe.util.util import ContentType
from templisafe.exceptions.binding_error import IllegalParamsDefinitionError, UnsupportedQVariantParserError

_PARAMS_KEY_KEY: str = 'params_key'
_DEFAULT_QVARIANT_KEY_KEY: str = 'default_variant_name'

VARIANT_PARSER_SETTINGS: str = f"""
default_diagnostic_policy: RAISE_WARNINGS
parser_type: YAML
{_PARAMS_KEY_KEY}: params
{_DEFAULT_QVARIANT_KEY_KEY}: default
"""

class VariantLoader(Loader):

    __slots__: tuple[str, ...] = ('_manager',)

    @staticmethod
    def _get_default_settings_source() -> InlineSource:
        settings: InlineSourceSettings = InlineSourceSettings(
            content_type=ContentType.YAML, 
            content=VARIANT_PARSER_SETTINGS
            )
        return InlineSource(settings)

    def __init__(self, default_settings_source: Source | None = None) -> None:
        super().__init__(
            default_settings_source or VariantLoader._get_default_settings_source()
        )
        self._manager: VariantParserManager = VariantParserManager()

    @overrides
    def _load_parser_settings(self, settings_source: Source, context: LoaderContext | None = None) -> VariantParserSettings:
        raw: str = settings_source.read()
        config: dict[str, Any] = self._load_config(raw, IllegalParamsDefinitionError)
        parser_type: ContentType = settings_source.content_type 
        try:
            match parser_type:
                case ContentType.YAML:
                    return YamlVariantParserSettings(
                        variants_key=config[_PARAMS_KEY_KEY],
                        default_variants_name=config[_DEFAULT_QVARIANT_KEY_KEY]
                    )
        except KeyError as e:
            raise IllegalParamsDefinitionError(f"Missing required key in params config: {e}") from e

        raise UnsupportedQVariantParserError(parser_type)

    def _create_settings(self, parser_settings_source: Source | None = None) -> VariantParserSettings:
        parser_settings: ParserSettings = (
            self._default_settings 
            if parser_settings_source is None 
            else self._load_parser_settings(parser_settings_source)
        ) 
        
        assert isinstance(parser_settings, VariantParserSettings)
        return parser_settings

    def load(self, params_source: Source, parser_settings_source: Source | None = None) -> VariantSet:
        parser_settings: VariantParserSettings = self._create_settings(parser_settings_source)
        parser: VariantParser = self._manager.get_or_create(parser_settings)
        return parser.parse(params_source.read())