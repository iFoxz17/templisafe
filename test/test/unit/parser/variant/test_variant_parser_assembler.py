from templisafe.core.util import DEFAULT_MANAGER_SETTINGS
from templisafe.parser.variant.variant_parser_assembler import VariantParserAssembler
from templisafe.parser.variant.variant_parser_manager import VariantParserManager
from templisafe.parser.variant.variant_parser_resolver import VariantParserResolver
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.settings.variant_parser_settings import VariantParserSettings

CUSTOM_MANAGER_SETTINGS_YAML = """
cache: false
"""

# -----------------------------
# Default settings
# -----------------------------
DEFAULT_VARIANT_PARSER_SETTINGS: VariantParserSettings = VariantParserSettings.create()


# -----------------------------
# Tests
# -----------------------------
def test_assemble_with_defaults():
    assembler = VariantParserAssembler()
    resolver: VariantParserResolver = assembler.assemble()

    assert isinstance(resolver, VariantParserResolver)
    assert isinstance(resolver._variant_parser_manager, VariantParserManager)
    assert resolver._variant_parser_manager._settings == DEFAULT_MANAGER_SETTINGS
    assert resolver._default_settings == DEFAULT_VARIANT_PARSER_SETTINGS


def test_assemble_with_custom_manager_settings():
    assembler = VariantParserAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    resolver = assembler.assemble(manager_settings=manager_settings)

    assert isinstance(resolver, VariantParserResolver)
    assert resolver._variant_parser_manager._settings == manager_settings


def test_assemble_with_custom_variant_parser_settings():
    assembler = VariantParserAssembler()
    custom_settings = VariantParserSettings.create(
        variants_key="vars",
        variant_name_key="name",
        bindings_key="bindings",
        default_variants_name="default",
    )
    resolver = assembler.assemble(default_variant_parser_settings=custom_settings)

    assert resolver._default_settings == custom_settings


def test_assemble_with_all_custom_settings():
    assembler = VariantParserAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    custom_variant_parser_settings = VariantParserSettings.create(
        variants_key="vars",
        variant_name_key="name",
        bindings_key="bindings",
        default_variants_name="default",
    )

    resolver = assembler.assemble(
        manager_settings=manager_settings,
        default_variant_parser_settings=custom_variant_parser_settings,
    )

    assert isinstance(resolver, VariantParserResolver)
    assert resolver._variant_parser_manager._settings == manager_settings
    assert resolver._default_settings == custom_variant_parser_settings
