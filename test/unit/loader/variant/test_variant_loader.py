import pytest

from templisafe.loader.variant.variant_loader import VariantLoader, VARIANT_PARSER_SETTINGS_YAML
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.exceptions.variant_error import IllegalVariantError
from templisafe.template.template_model import VariantSet


@pytest.fixture
def default_loader() -> VariantLoader:
    return VariantLoader()


@pytest.fixture
def custom_settings() -> VariantParserSettings:
    settings = VariantParserSettings.from_yaml(VARIANT_PARSER_SETTINGS_YAML)
    custom_settings = settings.model_copy(update={"variants_key": "params"})
    return custom_settings


def test_load_with_default_settings(default_loader: VariantLoader):
    variants_config = [
        {"variants": {"name": "v1", "bindings": {"a": 1}}},
        {"variants": {"name": "v2", "bindings": {"a": 2}}},
    ]
    variant_set = default_loader.load(variants_config)
    assert isinstance(variant_set, VariantSet)
    names = [v.name for v in variant_set.variants]
    assert names == ["v1", "v2"]


def test_load_with_custom_settings(custom_settings):
    loader = VariantLoader(custom_settings)
    variants_config = [{
        "params": [
            {"name": "alpha", "bindings": {"x": 10}},
            {"name": "beta", "bindings": {"x": 20}}
        ]
    }]
    variant_set = loader.load(variants_config)
    assert isinstance(variant_set, VariantSet)
    names = [v.name for v in variant_set.variants]
    assert names == ["alpha", "beta"]


def test_load_empty_list(default_loader: VariantLoader):
    empty_set = default_loader.load([])
    assert isinstance(empty_set, VariantSet)
    assert len(empty_set.variants) == 0


def test_load_invalid_config_raises(default_loader: VariantLoader):
    # Missing required "name" key
    invalid_config = [{"bindings": {"a": 1}}]
    with pytest.raises(IllegalVariantError):
        default_loader.load(invalid_config)

    # Wrong type for bindings
    invalid_config = [{"name": "v1", "bindings": "not a dict"}]
    with pytest.raises(IllegalVariantError):
        default_loader.load(invalid_config)


def test_resolve_settings_uses_default(default_loader: VariantLoader, custom_settings):
    # _resolve_settings returns default if None is passed
    resolved = default_loader._resolve_settings(None)
    assert resolved == default_loader._default_settings

    # Returns provided settings if not None
    resolved2 = default_loader._resolve_settings(custom_settings)
    assert resolved2 == custom_settings
