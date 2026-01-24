from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.renderer.renderer import Renderer

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class RendererFactory:
    """Creates `Renderer` instances from renderer settings."""

    __slots__: tuple[str, ...] = ()

    def create(self, settings: RendererSettings) -> Renderer:
        """Create a `Renderer` instance for the given settings."""

        return Renderer(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class RendererManager:
    """Manages the retrieval of `Renderer` instances."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_renderers")

    def __init__(
            self, 
            settings: ManagerSettings,
            factory: RendererFactory | None = None,
            renderers: dict[RendererSettings, Renderer] | None = None
            ) -> None:
        self._settings: ManagerSettings = settings
        self._factory: RendererFactory = factory or RendererFactory()
        self._renderers: dict[RendererSettings, Renderer] = renderers or {}
    
    def get_or_create(self, settings: RendererSettings) -> Renderer:
        """Return a `Renderer` instance according to the given settings."""
        
        c: dict[RendererSettings, Renderer] = self._renderers
        if settings in c:
            return c[settings]
        
        renderer: Renderer = self._factory.create(settings)
        if self._settings.cache:
            c[settings] = renderer
        return renderer

    def __contains__(self, settings: RendererSettings) -> bool:
        """Return whether a `Renderer` instance for the given settings is cached."""
        return settings in self._renderers