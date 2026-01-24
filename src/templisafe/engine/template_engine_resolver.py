from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.template_engine_manager import TemplateEngineManager
from templisafe.settings.template_engine_settings import TemplateEngineSettings

class TemplateEngineResolver:
    """Resolves `TemplateEngine` instances."""

    __slots__: tuple[str, ...] = ("_default_settings", "_template_engine_manager")

    def __init__(
            self, 
            default_settings: TemplateEngineSettings,
            template_engine_manager: TemplateEngineManager,
            ) -> None:
        self._default_settings: TemplateEngineSettings = default_settings
        self._template_engine_manager: TemplateEngineManager = template_engine_manager
        
    def resolve(self, template_engine: TemplateEngine | TemplateEngineSettings | None = None) -> TemplateEngine:
        """
        Resolve a `TemplateEngine` instance.

        This method supports three scenarios based on the type of the `template_engine` argument:
        1. If it is already a `TemplateEngine`, it is returned as-is.
        2. If it is a `TemplateEngineSettings`, a `TemplateEngine` based on the given settings is returned.
        3. If it is None, a `TemplateEngine` with default settings is returned.

        Parameters
        ----------
        template_engine : TemplateEngine | TemplateEngineSettings | None
            Either an existing engine, its settings or None to use the default engine.

        Returns
        -------
        TemplateEngine
            The resolved template engine instance.
        """

        if isinstance(template_engine, TemplateEngine):
            return template_engine
        
        settings: TemplateEngineSettings = template_engine or self._default_settings 
        return self._template_engine_manager.get_or_create(settings)