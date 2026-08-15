from templisafe.core.util import DEFAULT_MANAGER_SETTINGS
from templisafe.parser.schema.schema_parser_manager import (
    SchemaParserFactory,
    SchemaParserManager,
)
from templisafe.parser.schema.schema_parser_resolver import SchemaParserResolver
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.schema_parser_settings import SchemaParserSettings


class SchemaParserAssembler:
    """Assembles a `SchemaParserResolver` with all necessary components."""

    __slots__: tuple[str, ...] = ()

    def assemble(
        self,
        manager_settings: ManagerSettings | None = None,
        default_schema_parser_settings: SchemaParserSettings | None = None,
    ) -> SchemaParserResolver:
        """
        Create and return a fully initialized `SchemaParserResolver`.

        Parameters
        ----------
        manager_settings : ManagerSettings | None
            Optional manager settings. If not provided, default settings are used.
        default_schema_parser_settings : SchemaParserSettings | None
            Optional parser settings to use as default. If not provided, a default is used.

        Returns
        -------
        SchemaParserResolver
            A `SchemaParserResolver` ready to resolve schema parsers.
        """

        factory: SchemaParserFactory = SchemaParserFactory()
        manager: SchemaParserManager = SchemaParserManager(
            settings=manager_settings or DEFAULT_MANAGER_SETTINGS, factory=factory
        )
        resolver: SchemaParserResolver = SchemaParserResolver(
            schema_parser_manager=manager,
            default_settings=(default_schema_parser_settings or SchemaParserSettings.create()),
        )

        return resolver
