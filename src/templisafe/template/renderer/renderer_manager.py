from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.renderer.renderer import Renderer
from templisafe.engine.template_engine import TemplateEngine

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class RendererFactory:
    def create(self, settings: RendererSettings) -> Renderer:
        return Renderer(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class RendererManager:
    __slots__: tuple[str, ...] = ("_factory", "_renderers")

    def __init__(self, renderers: dict[RendererSettings, Renderer] | None = None) -> None:
        self._factory: RendererFactory = RendererFactory()
        self._renderers: dict[RendererSettings, Renderer] = renderers or {}
    
    def get_or_create(self, settings: RendererSettings) -> Renderer:
        c: dict[RendererSettings, Renderer] = self._renderers
        if settings not in c:
            c[settings] = self._factory.create(settings)
        return c[settings]

    def __contains__(self, settings: RendererSettings) -> bool:
        return settings in self._renderers