from types import MappingProxyType

from templisafe.engine.django_template_engine import DjangoTemplateEngine
from templisafe.engine.jinja_template_engine import JinjaTemplateEngine
from templisafe.engine.template_engine import TemplateEngine
from templisafe.exceptions.template_engine_error import UnsupportedTemplateEngineError
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.template_engine_settings import (
    TemplateEngineKind,
    TemplateEngineSettings,
)

# ---------------------------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------------------------


class TemplateEngineFactory:
    """Creates `TemplateEngine` instances from engine settings."""

    __slots__: tuple[str, ...] = ()

    _ENGINE_MAP: MappingProxyType[TemplateEngineKind, type[TemplateEngine]] = MappingProxyType(
        {
            TemplateEngineKind.JINJA: JinjaTemplateEngine,
            TemplateEngineKind.DJANGO: DjangoTemplateEngine,
        }
    )

    def __init__(self) -> None:
        pass

    def create(self, settings: TemplateEngineSettings) -> TemplateEngine:
        """Create a `TemplateEngine` instance for the given settings."""

        engine_type: type[TemplateEngine] | None = self._ENGINE_MAP.get(settings.engine_kind)
        if engine_type is None:
            raise UnsupportedTemplateEngineError(settings.engine_kind)
        return engine_type(settings)


# ---------------------------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------------------------


class TemplateEngineManager:
    """Manages the retrieval of `TemplateEngine` instances."""

    # __slots__: tuple[str, ...] = ("_settings", "_factory", "_engines")
    __slots__: tuple[str, ...] = ("_settings", "_factory")

    def __init__(
        self,
        settings: ManagerSettings,
        factory: TemplateEngineFactory | None = None,
        # engines: dict[TemplateEngineSettings, TemplateEngine] | None = None
    ) -> None:
        if settings.cache is True:
            raise ValueError("Caching not available for template engines")

        self._settings: ManagerSettings = settings
        self._factory: TemplateEngineFactory = factory or TemplateEngineFactory()
        # self._engines: dict[TemplateEngineSettings, TemplateEngine] = engines or {}

    def get_or_create(self, settings: TemplateEngineSettings) -> TemplateEngine:
        """Return a `TemplateEngine` instance according to the given settings."""
        return self._factory.create(settings)

    def __contains__(self, settings: TemplateEngineSettings) -> bool:
        """Return whether a `TemplateEngine` instance for the given settings is cached."""
        return False

    '''
    def get_or_create(self, settings: TemplateEngineSettings) -> TemplateEngine:
        """Return a `TemplateEngine` instance according to the given settings."""
        
        e: dict[TemplateEngineSettings, TemplateEngine] = self._engines
        if settings in e:
            return e[settings]
        
        engine: TemplateEngine = self._factory.create(settings)
        if self._settings.cache:
            e[settings] = engine
        return engine 

    def __contains__(self, settings: TemplateEngineSettings) -> bool:
        """Return whether a `TemplateEngine` instance for the given settings is cached."""

        return settings in self._engines
    '''
