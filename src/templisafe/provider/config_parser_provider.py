from templisafe.content.content import ContentType
from templisafe.parser.config.config_parser import ConfigParser
from templisafe.parser.config.config_parser_resolver import ConfigParserResolver

class ConfigParserProvider:
    """Provides `ConfigParser` instances for a given `ContentType`."""
    
    __slots__: tuple[str, ...] = ("_config_parser_resolver",)

    def __init__(self, config_parser_resolver: ConfigParserResolver) -> None:
        self._config_parser_resolver: ConfigParserResolver = config_parser_resolver

    def provide(self, content_type: ContentType) -> ConfigParser:
        """
        Provide a `ConfigParser` instance for the given content type.

        Parameters
        ----------
        content_type: ContentType
            The content type to retrieve the parser for.

        Returns
        -------
        ConfigParser
            The configuration parser instance for the given content type.
        """

        return self._config_parser_resolver.resolve(content_type)
        
