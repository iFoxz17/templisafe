from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.schema.schema_parser_resolver import SchemaParserResolver
from templisafe.settings.schema_parser_settings import SchemaParserSettings

class SchemaParserProvider:
    """Provides `SchemaParser` instances for a given settings."""
    
    __slots__: tuple[str, ...] = ("_schema_parser_resolver",)

    def __init__(self, schema_parser_resolver: SchemaParserResolver) -> None:
        self._schema_parser_resolver: SchemaParserResolver = schema_parser_resolver

    def provide(
            self, 
            schema_parser: SchemaParser | SchemaParserSettings | None = None
            ) -> SchemaParser:
        """
        Provide a `SchemaParser` instance for the given settings.

        Parameters
        ----------
        schema_parser: SchemaParser | SchemaParserSettings | None
            Optionally, a specific schema parser or settings. 

        Returns
        -------
        SchemaParser
            The schema parser instance for the given input.
        """

        return self._schema_parser_resolver.resolve(schema_parser)
        
