from templisafe.parser.config.config_parser import Config
from templisafe.parser.schema.schema_parser import Schema, SchemaParser


class SchemaProvider:
    """Provides `Schema` instances by delegating parsing to a `SchemaParser`."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def provide(self, config: Config, parser: SchemaParser) -> Schema:
        """
        Parse the given configuration into a `Schema` using the supplied parser.

        Parameters
        ----------
        config: Config
            The configuration to parse.
        parser: SchemaParser
            The parser responsible for interpreting the configuration.

        Returns
        -------
        Schema
            The parsed schema object.
        """

        return parser.parse(config)
