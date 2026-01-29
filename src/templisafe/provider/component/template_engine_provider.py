from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.template_engine_resolver import TemplateEngineResolver
from templisafe.settings.template_engine_settings import TemplateEngineSettings

class TemplateEngineProvider:
    """Provides `TemplateEngine` instances for a given settings."""
    
    __slots__: tuple[str, ...] = ("_template_engine_resolver",)

    def __init__(self, template_engine_resolver: TemplateEngineResolver) -> None:
        self._template_engine_resolver: TemplateEngineResolver = template_engine_resolver

    def provide(
            self, 
            template_engine: TemplateEngine | TemplateEngineSettings | None = None
            ) -> TemplateEngine:
        """
        Provide a `TemplateEngine` instance for the given settings.

        Parameters
        ----------
        template_engine: TemplateEngine | TemplateEngineSettings | None
            Optionally, a specific template engine or settings. 

        Returns
        -------
        TemplateEngine
            The template engine instance for the given input.
        """

        return self._template_engine_resolver.resolve(template_engine)
        
