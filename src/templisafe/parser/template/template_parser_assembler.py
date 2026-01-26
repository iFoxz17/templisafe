from templisafe.settings.manager_settings import ManagerSettings
from templisafe.parser.template.template_parser_resolver import TemplateParserResolver
from templisafe.util import DEFAULT_MANAGER_SETTINGS

class TemplateParserAssembler:
    """Assembles a `TemplateParserResolver` with all necessary components."""

    __slots__ : tuple[str, ...] = ()

    def assemble(
            self, 
            manager_settings: ManagerSettings | None = None,
            ) -> TemplateParserResolver:
        """
        Create and return a fully initialized `TemplateParserResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.
        
        Returns
        -------
        TemplateParserResolver
            A `TemplateParserResolver` ready to resolve template parsers.
        """

        resolver: TemplateParserResolver = TemplateParserResolver()
        return resolver
