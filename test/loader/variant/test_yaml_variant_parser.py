import pytest
from templisafe.loader.variant.yaml_variant_parser import YamlVariantParser
from templisafe.settings.parser.variant_parser_settings import YamlVariantParserSettings
from templisafe.template.template_model import Binding, VariantSet
from templisafe.exceptions.binding_error import IllegalVariantError

@pytest.fixture
def settings() -> YamlVariantParserSettings:
    return YamlVariantParserSettings(
        variants_key="variants",
        default_variants_name="default"
    )


def test_single_variant_yaml(settings):
    parser = YamlVariantParser(settings)
    yaml_str = """
variants:
  param1: 42
  param2: "abc"
"""
    vset: VariantSet = parser.parse(yaml_str)

    assert len(vset.variants) == 1
    variant = vset.variants[0]
    assert variant.names == {"param1", "param2"}

    b1: Binding | None = variant.get("param1")
    b2: Binding | None = variant.get("param2")
    assert b1 is not None
    assert b1.value == 42
    assert b1.index == 0
    assert b2 is not None
    assert b2.value == "abc"
    assert b2.index == 1


def test_multiple_variants_yaml(settings):
    parser = YamlVariantParser(settings)
    yaml_str = """
variants:
  variant1:
    param1: 1
    param2: "a"
  variant2:
    param1: 2
    param2: "b"
  variant3:
    param1: 
      - 1
      - 2
      - 3
    param2: "c"
"""
    vset: VariantSet = parser.parse(yaml_str)

    assert len(vset.variants) == 3
    assert {"variant1", "variant2", "variant3"} == vset.names
    assert all(isinstance(b, Binding) for v in vset.variants for b in v.bindings)
    variants = vset.variants
    for v in variants:
        bindings_names = v.names
        assert {"param1", "param2"} == bindings_names
    v3 = variants[2]
    v3_bvalues = [b.value for b in v3.bindings]
    assert [[1, 2, 3], "c"] == v3_bvalues


def test_illegal_yaml_structure(settings):
    parser = YamlVariantParser(settings)
    # Mixed single and dict values -> should raise TypeError
    yaml_str = """
variants:
  variant1:
    param1: 1
  variant2: 123
"""
    with pytest.raises(IllegalVariantError):
        parser.parse(yaml_str)


def test_missing_variants_key_yaml(settings):
    parser = YamlVariantParser(settings)
    yaml_str = """
wrong_key:
  param1: 1
"""
    with pytest.raises(IllegalVariantError):
        parser.parse(yaml_str)


def test_yaml_binding_indices(settings):
    parser = YamlVariantParser(settings)
    yaml_str = """
variants:
  paramA: 10
  paramB: 20
"""
    vset: VariantSet = parser.parse(yaml_str)
    variant = vset.variants[0]
    b_a = variant.get("paramA")
    b_b = variant.get("paramB")
    # Check indices are sequential in order of dict insertion
    assert b_a is not None
    assert b_b is not None
    assert b_a.index == 0
    assert b_b.index == 1
