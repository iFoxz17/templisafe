from templisafe.settings.manager_settings import ManagerSettings
from templisafe.parser.template.template_parser_resolver import TemplateParserResolver
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.util import DEFAULT_MANAGER_SETTINGS

class TemplateParserAssembler:
    """Assembles a `TemplateParserResolver` with all necessary components."""

    __slots__ : tuple[str, ...] = ()

    def assemble(
            self, 
            manager_settings: ManagerSettings | None = None,
            default_template_parser_settings: TemplateParserSettings | None = None
            ) -> TemplateParserResolver:
        """
        Create and return a fully initialized `TemplateParserResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.
        default_template_parser_settings : TemplateParserSettings | None
            Optional parser settings to use as default. If not provided, a default is used.
        
        Returns
        -------
        TemplateParserResolver
            A `TemplateParserResolver` ready to resolve template parsers.
        """

        resolver: TemplateParserResolver = TemplateParserResolver(
            default_template_parser_settings or TemplateParserSettings.create()
        )
        return resolver
