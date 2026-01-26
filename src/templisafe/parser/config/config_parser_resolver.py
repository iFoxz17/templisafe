from templisafe.parser.config.config_parser import ConfigParser
from templisafe.parser.config.config_parser_manager import ConfigParserManager
from templisafe.content.content import ContentType

class ConfigParserResolver:
    """Resolves `ConfigParser` instances."""

    __slots__: tuple[str, ...] = ("_config_parser_manager",)

    def __init__(
            self, 
            config_parser_manager: ConfigParserManager,
            ) -> None:
        self._config_parser_manager: ConfigParserManager = config_parser_manager
        
    def resolve(self, content_type: ContentType) -> ConfigParser:
        """
        Resolve a `ConfigParser` instance for a given content type.

        Parameters
        ----------
        content_type : ContentType
            The content type to resolve the config parser from.

        Returns
        -------
        ConfigParser
            The resolved configuration parser instance.
        """

        return self._config_parser_manager.get_or_create(content_type)