from templisafe.parser.config.config_parser import Config, ConfigParser

class ConfigProvider:
    """Provides `Config` instances by delegating parsing to a `ConfigParser`."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def provide(self, payload: str, parser: ConfigParser) -> Config:
        """
        Parse the given payload into a `Config` using the supplied parser.

        Parameters
        ----------
        payload: str
            The raw configuration payload to parse.
        parser: ConfigParser
            The parser responsible for interpreting the payload.

        Returns
        -------
        Config
            The parsed configuration object.
        """

        return parser.parse(payload)
