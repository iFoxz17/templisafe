import pytest
import yaml
import json

from templisafe.settings.parser.variant_parser_settings import VariantParserSettings, YamlVariantParserSettings
from templisafe.util.util import ContentType


def test_create_derived_class_without_kind():
    # Should create the base VariantParserSettings instance
    settings = YamlVariantParserSettings.create(
        variants_key="vars",
        default_variants_name="default"
    )
    assert isinstance(settings, VariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"

def test_create_base_class_without_kind_raises():
    with pytest.raises(ValueError):
        settings = VariantParserSettings.create(
            variants_key="vars",
            default_variants_name="default"
        )

def test_create_base_class_with_kind_dispatch():
    # Dispatch to YAML concrete subclass
    settings = VariantParserSettings.create(
        kind=ContentType.YAML,
        variants_key="vars",
        default_variants_name="default"
    )
    assert isinstance(settings, YamlVariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"
    assert settings.kind == ContentType.YAML


def test_create_invalid_kind():
    with pytest.raises(ValueError, match="Invalid kind: 'invalid'"):
        VariantParserSettings.create(
            kind="invalid",
            variants_key="vars",
            default_variants_name="default"
        )


def test_create_unregistered_kind():
    class DummyParserSettings(VariantParserSettings):
        pass

    with pytest.raises(ValueError, match="No VariantParserSettings registered for kind"):
        DummyParserSettings.create(
            kind=ContentType.TEXT,
            variants_key="vars",
            default_variants_name="default"
        )


def test_create_missing_variants_key():
    with pytest.raises(ValueError):
        YamlVariantParserSettings.create(default_variants_name="default")


def test_create_missing_default_variants_name():
    with pytest.raises(ValueError):
        YamlVariantParserSettings.create(variants_key="vars")


def test_from_dict_dispatch():
    config = {
        "kind": ContentType.YAML,
        "variants_key": "vars",
        "default_variants_name": "default"
    }
    settings = VariantParserSettings.from_dict(config)
    assert isinstance(settings, YamlVariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"
    assert settings.kind == ContentType.YAML


def test_from_yaml_string_dispatch():
    yaml_str = """
kind: YAML
variants_key: vars
default_variants_name: default
"""
    settings = VariantParserSettings.from_yaml(yaml_str)
    assert isinstance(settings, YamlVariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"
    assert settings.kind == ContentType.YAML


def test_from_json_string_dispatch():
    json_str = json.dumps({
        "kind": "YAML",
        "variants_key": "vars",
        "default_variants_name": "default"
    })
    settings = VariantParserSettings.from_json(json_str)
    assert isinstance(settings, YamlVariantParserSettings)
    assert settings.variants_key == "vars"
    assert settings.default_variants_name == "default"
    assert settings.kind == ContentType.YAML