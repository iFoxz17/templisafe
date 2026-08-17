from templisafe.parser.schema.schema_parser import SchemaParser
from templisafe.parser.schema.schema_parser_manager import SchemaParserManager
from templisafe.settings.schema_parser_settings import SchemaParserSettings


class SchemaParserResolver:
    """Resolves `SchemaParser` instances."""

    __slots__: tuple[str, ...] = ("_default_settings", "_schema_parser_manager")

    def __init__(
        self,
        default_settings: SchemaParserSettings,
        schema_parser_manager: SchemaParserManager,
    ) -> None:
        self._default_settings: SchemaParserSettings = default_settings
        self._schema_parser_manager: SchemaParserManager = schema_parser_manager

    def resolve(self, schema_parser: SchemaParser | SchemaParserSettings | None = None) -> SchemaParser:
        """
        Resolve a `SchemaParser` instance.

        This method supports three scenarios based on the type of the `schema_parser` argument:
        1. If it is already a `SchemaParser`, it is returned as-is.
        2. If it is a `SchemaParserSettings`, a `SchemaParser` based on the given settings is returned.
        3. If it is None, a `SchemaParser` with default settings is returned.

        Parameters
        ----------
        schema_parser : SchemaParser | SchemaParserSettings | None
            Either an existing schema parser, its settings or None to use the default schema parser.

        Returns
        -------
        SchemaParser
            The resolved schema parser instance.
        """

        if isinstance(schema_parser, SchemaParser):
            return schema_parser

        settings: SchemaParserSettings = schema_parser or self._default_settings
        return self._schema_parser_manager.get_or_create(settings)
