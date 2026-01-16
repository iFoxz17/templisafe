from types import MappingProxyType

from templisafe.settings.template_engine_settings import TemplateEngineKind, TemplateEngineSettings
from templisafe.engine.template_engine import TemplateEngine
from templisafe.engine.jinja_template_engine import JinjaTemplateEngine
from templisafe.engine.django_template_engine import DjangoTemplateEngine
from templisafe.engine.custom_template_engine import CustomTemplateEngine

from templisafe.exceptions.template_engine_error import UnsupportedTemplateEngineError

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class TemplateEngineFactory:
    """Creates TemplateEngine instances from engine settings."""

    __slots__: tuple[str, ...] = ()

    _ENGINE_MAP: MappingProxyType[TemplateEngineKind, type[TemplateEngine]] = MappingProxyType({
        TemplateEngineKind.JINJA: JinjaTemplateEngine,
        TemplateEngineKind.DJANGO: DjangoTemplateEngine,
        TemplateEngineKind.CUSTOM: CustomTemplateEngine
    })
    
    def __init__(self) -> None:
        pass

    def create(self, settings: TemplateEngineSettings) -> TemplateEngine:
        """Create a TemplateEngine instance for the given settings."""

        engine_type: type[TemplateEngine] | None = self._ENGINE_MAP.get(settings.kind)
        if engine_type is None:
            raise UnsupportedTemplateEngineError(settings.kind)
        return engine_type(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class TemplateEngineManager:
    """
    Manages TemplateEngine instances.
    At the moment no caching is performed: a new engine is created each time.
    """

    __slots__: tuple[str, ...] = ("_factory",)

    def __init__(self) -> None:
        self._factory: TemplateEngineFactory = TemplateEngineFactory()

    def get_or_create(self, settings: TemplateEngineSettings) -> TemplateEngine:
        """
        Create a new TemplateEngine instance for the given settings.
        """

        return self._factory.create(settings)
