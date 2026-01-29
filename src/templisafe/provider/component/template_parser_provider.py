from templisafe.parser.template.template_parser import TemplateParser
from templisafe.parser.template.template_parser_resolver import TemplateParserResolver
from templisafe.settings.template_parser_settings import TemplateParserSettings

class TemplateParserProvider:
    """Provides `TemplateParser` instances for a given settings."""
    
    __slots__: tuple[str, ...] = ("_template_parser_resolver",)

    def __init__(self, template_parser_resolver: TemplateParserResolver) -> None:
        self._template_parser_resolver: TemplateParserResolver = template_parser_resolver

    def provide(
            self, 
            template_parser_settings: TemplateParserSettings | None = None
            ) -> TemplateParser:
        """
        Provide a `TemplateParser` instance for the given settings.

        Parameters
        ----------
        template_parser: TemplateParserSettings | None
            Optionally, a specific template parser settings.

        Returns
        -------
        TemplateParser
            The template parser instance for the given input.
        """

        return self._template_parser_resolver.resolve(template_parser_settings)
        
