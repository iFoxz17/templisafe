from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.renderer.renderer_manager import RendererManager


class RendererResolver:
    """Resolves `Renderer` instances."""

    __slots__: tuple[str, ...] = ("_default_settings", "_renderer_manager")

    def __init__(
        self,
        default_settings: RendererSettings,
        renderer_manager: RendererManager,
    ) -> None:
        self._default_settings: RendererSettings = default_settings
        self._renderer_manager: RendererManager = renderer_manager

    def resolve(self, renderer: Renderer | RendererSettings | None = None) -> Renderer:
        """
        Resolve a `Renderer` instance.

        This method supports three scenarios based on the type of the `renderer` argument:
        1. If it is already a `Renderer`, it is returned as-is.
        2. If it is a `RendererSettings`, a `Renderer` based on the given settings is returned.
        3. If it is None, a `Renderer` with default settings is returned.

        Parameters
        ----------
        renderer : Renderer | RendererSettings | None
            Either an existing renderer, its settings or None to use the default renderer.

        Returns
        -------
        Renderer
            The resolved renderer instance.
        """

        if isinstance(renderer, Renderer):
            return renderer

        settings: RendererSettings = renderer or self._default_settings
        return self._renderer_manager.get_or_create(settings)
