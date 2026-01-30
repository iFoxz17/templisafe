from templisafe.parser.config.config_parser import Config
from templisafe.parser.variant.variant_parser import VariantSet, VariantParser

class VariantProvider:
    """Provides `Variant` instances by delegating parsing to a `VariantParser`."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def provide(self, config: Config, parser: VariantParser) -> VariantSet:
        """
        Parse the given configuration into a `VariantSet` using the supplied parser.

        Parameters
        ----------
        config: Config
            The configuration to parse.
        parser: VariantParser
            The parser responsible for interpreting the configuration.

        Returns
        -------
        VariantSet
            The set of parsed variant objects.
        """

        return parser.parse(config)
