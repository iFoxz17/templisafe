from templisafe.parser.variant.variant_parser import VariantParser
from templisafe.parser.variant.variant_parser_resolver import VariantParserResolver
from templisafe.settings.variant_parser_settings import VariantParserSettings

class VariantParserProvider:
    """Provides `VariantParser` instances for a given settings."""
    
    __slots__: tuple[str, ...] = ("_variant_parser_resolver",)

    def __init__(self, variant_parser_resolver: VariantParserResolver) -> None:
        self._variant_parser_resolver: VariantParserResolver = variant_parser_resolver

    def provide(
            self, 
            variant_parser: VariantParser | VariantParserSettings | None = None
            ) -> VariantParser:
        """
        Provide a `VariantParser` instance for the given settings.

        Parameters
        ----------
        variant_parser: VariantParser | VariantParserSettings | None
            Optionally, a specific variant parser or settings. 

        Returns
        -------
        VariantParser
            The variant parser instance for the given input.
        """

        return self._variant_parser_resolver.resolve(variant_parser)
        
