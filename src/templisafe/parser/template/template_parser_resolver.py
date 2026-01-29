from templisafe.parser.template.template_parser import TemplateParser
from templisafe.settings.template_parser_settings import TemplateParserSettings

class TemplateParserResolver:
    """Resolves `TemplateParser` instances."""

    __slots__: tuple[str, ...] = ("_default_settings",)

    def __init__(self, default_settings: TemplateParserSettings) -> None:
        self._default_settings: TemplateParserSettings = default_settings
        
    def resolve(self, settings: TemplateParserSettings | None = None) -> TemplateParser:
        """
        Resolve a `TemplateParser` instance for a given settings.

        Parameters
        ----------
        settings : TemplateParserSettings
            The settings to resolve the template parser from. 
            If `None`, the default settings are used.

        Returns
        -------
        TemplateParser
            The resolved template parser instance.
        """

        return TemplateParser(settings or self._default_settings )