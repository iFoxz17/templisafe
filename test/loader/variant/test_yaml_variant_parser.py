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

# -----------------------------
# Implicit variant tests
# -----------------------------
def test_single_implicit_variant_yaml(settings):
    parser = YamlVariantParser(settings)
    yaml_str = """
variants:
  param1: 42
  param2: "abc"
"""
    vset: VariantSet = parser.parse([yaml_str])

    # Only one implicit variant: default_1
    assert len(vset.variants) == 1
    variant = vset.variants[0]
    assert variant.name == "default_1"
    assert variant.names == {"param1", "param2"}

    b1 = variant.get("param1")
    b2 = variant.get("param2")
    assert b1 is not None
    assert b1.value == 42 and b1.index == 0
    assert b2 is not None
    assert b2.value == "abc" and b2.index == 1

# -----------------------------
# Explicit variant tests
# -----------------------------
def test_multiple_explicit_variants_one_yaml(settings):
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
    vset: VariantSet = parser.parse([yaml_str])

    assert len(vset.variants) == 3
    assert vset.names == {"variant1", "variant2", "variant3"}

    for variant in vset.variants:
        assert all(isinstance(b, Binding) for b in variant.bindings)
        assert variant.names == {"param1", "param2"}

    v3 = next(v for v in vset.variants if v.name == "variant3")
    values = [b.value for b in v3.bindings]
    assert values == [[1, 2, 3], "c"]

# -----------------------------
# Multiple implicit variants
# -----------------------------
def test_multiple_implicit_variants_multiple_yaml(settings):
    parser = YamlVariantParser(settings)
    yaml_str1 = """
variants:
  param1: 1
"""
    yaml_str2 = """
variants:
  param1: 2
"""
    vset: VariantSet = parser.parse([yaml_str1, yaml_str2])

    # Each implicit YAML should produce a separate default variant
    assert vset.names == {"default_1", "default_2"}
    v1 = next(v for v in vset.variants if v.name == "default_1")
    v2 = next(v for v in vset.variants if v.name == "default_2")
    v1_binding = v1.get("param1")
    v2_binding = v2.get("param1")
    assert v1_binding is not None
    assert v2_binding is not None
    assert v1_binding.value == 1
    assert v2_binding.value == 2

# -----------------------------
# Mixed explicit + implicit
# -----------------------------
def test_multiple_explicit_variants_multiple_yaml(settings):
    parser = YamlVariantParser(settings)
    expl_yaml1_str = """
variants:
  explicit1:
    param1: 100
    param2: foo
"""
    expl_yaml2_str = """
variants:
  explicit2:
    param1: 200
    param2: bar
  explicit3:
    param1: 300
    param2: zet
"""
    vset: VariantSet = parser.parse([expl_yaml1_str, expl_yaml2_str])

    # One implicit default + explicit variant
    assert vset.names == {"explicit1", "explicit2", "explicit3"}

    implicit_variant = next(v for v in vset.variants if v.name == "explicit1")
    param1 = implicit_variant.get("param1")
    param2 = implicit_variant.get("param2")
    assert param1 is not None 
    assert param2 is not None 
    assert param1.value == 100
    assert param2.value == "foo"

    explicit_variant_1 = next(v for v in vset.variants if v.name == "explicit2")
    param1 = explicit_variant_1.get("param1")
    param2 = explicit_variant_1.get("param2")
    assert param1 is not None 
    assert param2 is not None 
    assert param1.value == 200
    assert param2.value == "bar"

    explicit_variant_2 = next(v for v in vset.variants if v.name == "explicit3")
    param1 = explicit_variant_2.get("param1")
    param2 = explicit_variant_2.get("param2")
    assert param1 is not None 
    assert param2 is not None 
    assert param1.value == 300
    assert param2.value == "zet"


# -----------------------------
# Mixed explicit + implicit
# -----------------------------
def test_mixed_implicit_and_explicit_variants(settings):
    parser = YamlVariantParser(settings)
    impl_yaml_str = """
variants:
  param1: 100
  param2: foo
"""
    expl_yaml_str = """
variants:
  explicit1:
    param1: 200
    param2: bar
  explicit2:
    param1: 300
    param2: zet
"""
    vset: VariantSet = parser.parse([impl_yaml_str, expl_yaml_str])

    # One implicit default + explicit variant
    assert vset.names == {"default_1", "explicit1", "explicit2"}

    implicit_variant = next(v for v in vset.variants if v.name == "default_1")
    param1 = implicit_variant.get("param1")
    param2 = implicit_variant.get("param2")
    assert param1 is not None 
    assert param2 is not None 
    assert param1.value == 100
    assert param2.value == "foo"

    explicit_variant_1 = next(v for v in vset.variants if v.name == "explicit1")
    param1 = explicit_variant_1.get("param1")
    param2 = explicit_variant_1.get("param2")
    assert param1 is not None 
    assert param2 is not None 
    assert param1.value == 200
    assert param2.value == "bar"

    explicit_variant_2 = next(v for v in vset.variants if v.name == "explicit2")
    param1 = explicit_variant_2.get("param1")
    param2 = explicit_variant_2.get("param2")
    assert param1 is not None 
    assert param2 is not None 
    assert param1.value == 300
    assert param2.value == "zet"

# -----------------------------
# Duplicate variant names
# -----------------------------
def test_duplicate_variant_name_raises(settings):
    parser = YamlVariantParser(settings)
    yaml_expl1_str = """
variants:
  variant1:
    a: 1
"""

    yaml_expl2_str = """
variants:
  variant1:
    a: 2
"""
    with pytest.raises(IllegalVariantError):
      parser.parse([yaml_expl1_str, yaml_expl2_str])

# -----------------------------
# Missing top-level variants key
# -----------------------------
def test_missing_variants_key_yaml(settings):
    parser = YamlVariantParser(settings)
    yaml_str = """
wrong_key:
  param1: 1
"""
    with pytest.raises(IllegalVariantError, match="Missing top-level variants key"):
        parser.parse([yaml_str])

# -----------------------------
# Binding indices
# -----------------------------
def test_yaml_binding_indices(settings):
    parser = YamlVariantParser(settings)
    yaml_str = """
variants:
  paramA: 10
  paramB: 20
"""
    vset: VariantSet = parser.parse([yaml_str])
    variant = vset.variants[0]

    b_a = variant.get("paramA")
    b_b = variant.get("paramB")
    assert b_a is not None
    assert b_b is not None
    assert b_a.index == 0
    assert b_b.index == 1
