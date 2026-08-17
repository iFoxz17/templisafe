from templisafe.core.util import DEFAULT_MANAGER_SETTINGS
from templisafe.parser.variant.variant_parser_manager import (
    VariantParserFactory,
    VariantParserManager,
)
from templisafe.parser.variant.variant_parser_resolver import VariantParserResolver
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings


class VariantParserAssembler:
    """Assembles a `VariantParserResolver` with all necessary components."""

    __slots__: tuple[str, ...] = ()

    def assemble(
        self,
        manager_settings: ManagerSettings | None = None,
        default_variant_parser_settings: VariantParserSettings | None = None,
    ) -> VariantParserResolver:
        """
        Create and return a fully initialized `VariantParserResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.
        default_variant_parser_settings : VariantParserSettings | None
            Optional parser settings to use as default. If not provided, a default is used.

        Returns
        -------
        VariantParserResolver
            A `VariantParserResolver` ready to resolve variant parsers.
        """

        factory: VariantParserFactory = VariantParserFactory()
        manager: VariantParserManager = VariantParserManager(
            settings=manager_settings or DEFAULT_MANAGER_SETTINGS, factory=factory
        )
        resolver: VariantParserResolver = VariantParserResolver(
            variant_parser_manager=manager,
            default_settings=(default_variant_parser_settings or VariantParserSettings.create()),
        )

        return resolver
