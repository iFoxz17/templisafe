from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.parser.variant.variant_parser_manager import VariantParserManager
from templisafe.settings.variant_parser_settings import VariantParserSettings

class VariantParserResolver:
    """Resolves `VariantParser` instances."""

    __slots__: tuple[str, ...] = ("_default_settings", "_variant_parser_manager")

    def __init__(
            self, 
            default_settings: VariantParserSettings,
            variant_parser_manager: VariantParserManager,
            ) -> None:
        self._default_settings: VariantParserSettings = default_settings
        self._variant_parser_manager: VariantParserManager = variant_parser_manager
        
    def resolve(self, variant_parser: VariantParser | VariantParserSettings | None = None) -> VariantParser:
        """
        Resolve a `VariantParser` instance.

        This method supports three scenarios based on the type of the `variant_parser` argument:
        1. If it is already a `VariantParser`, it is returned as-is.
        2. If it is a `VariantParserSettings`, a `VariantParser` based on the given settings is returned.
        3. If it is None, a `VariantParser` with default settings is returned.

        Parameters
        ----------
        variant_parser : VariantParser | VariantParserSettings | None
            Either an existing variant parser, its settings or None to use the default variant parser.

        Returns
        -------
        VariantParser
            The resolved variant parser instance.
        """

        if isinstance(variant_parser, VariantParser):
            return variant_parser
        
        settings: VariantParserSettings = variant_parser or self._default_settings 
        return self._variant_parser_manager.get_or_create(settings)