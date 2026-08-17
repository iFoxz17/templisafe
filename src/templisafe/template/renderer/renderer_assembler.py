from templisafe.core.util import DEFAULT_MANAGER_SETTINGS
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.template.renderer.renderer_manager import (
    RendererFactory,
    RendererManager,
)
from templisafe.template.renderer.renderer_resolver import RendererResolver


class RendererAssembler:
    """Assembles a `RendererResolver` with all necessary components."""

    __slots__: tuple[str, ...] = ()

    def assemble(
        self,
        manager_settings: ManagerSettings | None = None,
        default_renderer_settings: RendererSettings | None = None,
    ) -> RendererResolver:
        """
        Create and return a fully initialized `RendererResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.
        default_renderer_settings : RendererSettings | None
            Optional engine settings to use as default. If not provided, a default is used.

        Returns
        -------
        RendererResolver
            A `RendererResolver` ready to resolve engines.
        """

        factory: RendererFactory = RendererFactory()
        manager: RendererManager = RendererManager(
            settings=manager_settings or DEFAULT_MANAGER_SETTINGS, factory=factory
        )
        resolver: RendererResolver = RendererResolver(
            renderer_manager=manager,
            default_settings=(default_renderer_settings or RendererSettings.create()),
        )

        return resolver
