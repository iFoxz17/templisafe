from templisafe.template.renderer.renderer import Renderer
from templisafe.template.renderer.renderer_resolver import RendererResolver
from templisafe.settings.renderer_settings import RendererSettings

class RendererProvider:
    """Provides `Renderer` instances for a given settings."""
    
    __slots__: tuple[str, ...] = ("_renderer_resolver",)

    def __init__(self, renderer_resolver: RendererResolver) -> None:
        self._renderer_resolver: RendererResolver = renderer_resolver

    def provide(
            self, 
            renderer: Renderer | RendererSettings | None = None
            ) -> Renderer:
        """
        Provide a `Renderer` instance for the given settings.

        Parameters
        ----------
        renderer: Renderer | RendererSettings | None
            Optionally, a specific renderer or settings. 

        Returns
        -------
        Renderer
            The renderer instance for the given input.
        """

        return self._renderer_resolver.resolve(renderer)
    