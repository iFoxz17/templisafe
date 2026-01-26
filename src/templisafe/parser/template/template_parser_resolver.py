from templisafe.parser.template.template_parser import TemplateParser
from templisafe.settings.template_parser_settings import TemplateParserSettings

class TemplateParserResolver:
    """Resolves `TemplateParser` instances."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass
        
    def resolve(self, settings: TemplateParserSettings) -> TemplateParser:
        """
        Resolve a `TemplateParser` instance for a given settinfs.

        Parameters
        ----------
        settings : TemplateParserSettings
            The settings to resolve the template parser from.

        Returns
        -------
        TemplateParser
            The resolved template parser instance.
        """

        return TemplateParser(settings)