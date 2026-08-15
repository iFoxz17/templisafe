import json

import pytest
import yaml

from templisafe.content.content import ContentType
from templisafe.exceptions.settings_error import SettingsError
from templisafe.settings.settings import Settings
from templisafe.settings.variant_parser_settings import VariantParserSettings


def test_create_defaults():
    settings = VariantParserSettings.create()
    assert isinstance(settings, VariantParserSettings)
    assert settings.variants_key == "variants"
    assert settings.default_variants_name == "default"
    assert settings.variant_name_key == "name"
    assert settings.bindings_key == "bindings"


def test_create_derived_class_without_kind():
    # Should create the base VariantParserSettings instance
    settings = VariantParserSettings.create(
        variants_key="vars",
        default_variants_name="default",
        variant_name_key="name",
        bindings_key="bindings",
    )
    assert isinstance(settings, VariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"
    assert settings.variant_name_key == "name"
    assert settings.bindings_key == "bindings"


def test_create_base_class_without_kind_raises():
    with pytest.raises(SettingsError):
        test = Settings.create(
            variants_key="vars",
            default_variants_name="default",
            variant_name_key="name",
            bindings_key="bindings",
        )
        a = 1


def test_create_base_class_with_kind_dispatch():
    # Dispatch to YAML concrete subclass
    settings = VariantParserSettings.create(
        variants_key="vars",
        default_variants_name="default",
        variant_name_key="name",
        bindings_key="bindings",
    )
    assert isinstance(settings, VariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"
    assert settings.variant_name_key == "name"
    assert settings.bindings_key == "bindings"


def test_create_invalid_kind():
    with pytest.raises(SettingsError):
        VariantParserSettings.create(
            kind="invalid",
            variants_key="vars",
            default_variants_name="default",
            variant_name_key="name",
            bindings_key="bindings",
        )


def test_from_dict_dispatch():
    config = {
        "variants_key": "vars",
        "default_variants_name": "default",
        "variant_name_key": "name",
        "bindings_key": "bindings",
    }
    settings = VariantParserSettings.from_dict(config)
    assert isinstance(settings, VariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"
    assert settings.variant_name_key == "name"
    assert settings.bindings_key == "bindings"


def test_from_yaml_string_dispatch():
    yaml_str = """
variants_key: vars
default_variants_name: default
variant_name_key: name
bindings_key: bindings
"""
    settings = VariantParserSettings.from_yaml(yaml_str)
    assert isinstance(settings, VariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"
    assert settings.variant_name_key == "name"
    assert settings.bindings_key == "bindings"


def test_from_json_string_dispatch():
    json_str = json.dumps(
        {
            "variants_key": "vars",
            "default_variants_name": "default",
            "variant_name_key": "name",
            "bindings_key": "bindings",
        }
    )
    settings = VariantParserSettings.from_json(json_str)
    assert isinstance(settings, VariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"
    assert settings.variant_name_key == "name"
    assert settings.bindings_key == "bindings"
