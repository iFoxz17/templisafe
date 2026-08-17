import json

import pytest

from templisafe.exceptions.settings_error import SettingsError
from templisafe.settings.settings import Settings
from templisafe.settings.variant_parser_settings import VariantParserSettings


def test_create_defaults():
    settings = VariantParserSettings.create()
    assert isinstance(settings, VariantParserSettings)
    assert settings.default_variants_name == "default"


def test_create_with_custom_default_name():
    settings = VariantParserSettings.create(default_variants_name="case")
    assert isinstance(settings, VariantParserSettings)
    assert settings.default_variants_name == "case"


def test_create_base_class_without_kind_raises():
    with pytest.raises(SettingsError):
        Settings.create(default_variants_name="case")


def test_create_base_class_with_kind_dispatch():
    settings = Settings.create(kind="variant_parser_settings", default_variants_name="case")
    assert isinstance(settings, VariantParserSettings)
    assert settings.default_variants_name == "case"


def test_create_invalid_kind():
    with pytest.raises(SettingsError):
        VariantParserSettings.create(kind="invalid", default_variants_name="case")


def test_from_dict_dispatch():
    settings = VariantParserSettings.from_dict({"default_variants_name": "case"})
    assert isinstance(settings, VariantParserSettings)
    assert settings.default_variants_name == "case"


def test_from_yaml_string_dispatch():
    settings = VariantParserSettings.from_yaml("default_variants_name: case")
    assert isinstance(settings, VariantParserSettings)
    assert settings.default_variants_name == "case"


def test_from_json_string_dispatch():
    settings = VariantParserSettings.from_json(json.dumps({"default_variants_name": "case"}))
    assert isinstance(settings, VariantParserSettings)
    assert settings.default_variants_name == "case"


def test_legacy_custom_document_key_settings_raise():
    with pytest.raises(SettingsError):
        VariantParserSettings.create(variants_key="cases")
