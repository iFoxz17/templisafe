from overrides import overrides
from typing import Any

from sqltemplater.query.query_model import QVariantSet
from sqltemplater.loader.variant.qvariant_parser import QVariantParser
from sqltemplater.source.source import Source
from sqltemplater.source.content_source import ContentSource
from sqltemplater.settings.source_settings import ContentSourceSettings
from sqltemplater.loader.variant.qvariant_parser_manager import QVariantParserManager
from sqltemplater.loader.qloader import QLoader, QLoaderContext
from sqltemplater.settings.parser.qparser_settings import QParserSettings
from sqltemplater.settings.parser.qparams_parser_settings import YamlQVariantParserSettings, QVariantParserSettings
from sqltemplater.util.util import ContentType
from sqltemplater.exceptions.binding_error import IllegalParamsDefinitionError, UnsupportedQVariantParserError

QVARIANT_PARSER_SETTINGS: str = f"""
default_diagnostic_policy: RAISE_WARNINGS
parser_type: YAML
params_key: params
default_variant_name: default
"""

class QVariantLoader(QLoader):

    _PARAMS_KEY_KEY: str = 'params_key'
    _DEFAULT_QVARIANT_KEY_KEY: str = 'default_variant_name'

    __slots__: tuple[str, ...] = ('_manager',)

    @staticmethod
    def _get_default_settings_source() -> ContentSource:
        settings: ContentSourceSettings = ContentSourceSettings(ContentType.YAML, QVARIANT_PARSER_SETTINGS)
        return ContentSource(settings)

    def __init__(self, default_settings_source: Source | None = None) -> None:
        super().__init__(
            default_settings_source or QVariantLoader._get_default_settings_source()
        )
        self._manager: QVariantParserManager = QVariantParserManager()

    @overrides
    def _load_parser_settings(self, settings_source: Source, context: QLoaderContext | None = None) -> QVariantParserSettings:
        raw: str = settings_source.read()
        config: dict[str, Any] = self._load_config(raw, IllegalParamsDefinitionError)
        parser_type: ContentType = settings_source.content_type 
        try:
            match parser_type:
                case ContentType.YAML:
                    return YamlQVariantParserSettings(
                        variants_key=config[QVariantLoader._PARAMS_KEY_KEY],
                        default_variants_name=config[QVariantLoader._DEFAULT_QVARIANT_KEY_KEY]
                    )
        except KeyError as e:
            raise IllegalParamsDefinitionError(f"Missing required key in params config: {e}") from e

        raise UnsupportedQVariantParserError(parser_type)

    def _create_settings(self, parser_settings_source: Source | None = None) -> QVariantParserSettings:
        parser_settings: QParserSettings = (
            self._default_settings 
            if parser_settings_source is None 
            else self._load_parser_settings(parser_settings_source)
        ) 
        
        assert isinstance(parser_settings, QVariantParserSettings)
        return parser_settings

    def load(self, params_source: Source, parser_settings_source: Source | None = None) -> QVariantSet:
        parser_settings: QVariantParserSettings = self._create_settings(parser_settings_source)
        parser: QVariantParser = self._manager.get_or_create(parser_settings)
        return parser.parse(params_source.read())