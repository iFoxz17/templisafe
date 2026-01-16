import pytest
import yaml

from templisafe.loader.variant.variant_parser import VariantParser
from templisafe.settings.variant_parser_settings import VariantParserSettings
from templisafe.template.template_model import Binding, VariantSet
from templisafe.exceptions.variant_error import IllegalVariantError

@pytest.fixture
def settings() -> VariantParserSettings:
    return VariantParserSettings(
        variants_key="variants",
        default_variants_name="default",
        variant_name_key="name",
        bindings_key="bindings"
    )

def safe_load(yaml_str: str) -> dict:
    """Load YAML safely, fallback to empty dict if None"""
    cfg = yaml.safe_load(yaml_str)
    return cfg if cfg is not None else {}

# -----------------------------
# Implicit variant tests
# -----------------------------

def test_single_implicit_variant_without_name_yaml(settings):
    parser = VariantParser(settings)
    yaml_str = """
variants:
  param1: 42
  param2: "abc"
"""
    yaml_cfg = yaml.safe_load(yaml_str)
    vset: VariantSet = parser.parse([yaml_cfg])

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

def test_implicit_variant_without_name_complex_object(settings):
    parser = VariantParser(settings)
    yaml_str = """
variants: 
    a:
      - a1:
        - 1
      - a2:
        - 2
        - 2.1
      - a3:
        - 3
        - 3.1
        - 3.2
    b:
      - b1: [4, 4.1, 4.2, 4.3]
      - b2: [5, 5.1, 5.2, 5.3, 5.4]
      - b3: [6, 6.1, 6.2, 6.3, 6.4, 6.5]
"""
    a: list[dict[str, list[float]]] = [
            {"a1": [1]},
            {"a2": [2, 2.1]},
            {"a3": [3, 3.1, 3.2]}
        ]
        
        
    b: list[dict[str, list[float]]] = [
            {"b1": [4, 4.1, 4.2, 4.3]},
            {"b2": [5, 5.1, 5.2, 5.3, 5.4]},
            {"b3": [6, 6.1, 6.2, 6.3, 6.4, 6.5]}
        ]
    
    yaml_cfg = yaml.safe_load(yaml_str)
    vset: VariantSet = parser.parse([yaml_cfg])

    assert len(vset.variants) == 1
    assert vset.names == {"default_1"}

    for variant, b_names in zip(vset.variants, [{"a", "b"}]):
        assert all(isinstance(b, Binding) for b in variant.bindings)
        assert variant.names == set(b_names)

    v = next(v for v in vset.variants if v.name == "default_1")
    values = [b.value for b in v.bindings]
    assert values == [a, b]

def test_multiple_implicit_variants_one_yaml(settings):
    parser = VariantParser(settings)
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
    yaml_cfg = yaml.safe_load(yaml_str)
    vset: VariantSet = parser.parse([yaml_cfg])

    assert len(vset.variants) == 3
    assert vset.names == {"variant1", "variant2", "variant3"}

    for variant in vset.variants:
        assert all(isinstance(b, Binding) for b in variant.bindings)
        assert variant.names == {"param1", "param2"}

    v3 = next(v for v in vset.variants if v.name == "variant3")
    values = [b.value for b in v3.bindings]
    assert values == [[1, 2, 3], "c"]

def test_implicit_variant_with_name_complex_object(settings):
    parser = VariantParser(settings)
    yaml_str = """
variants:
  variant1:
    complex: 
      a:
        - a1:
          - 1
        - a2:
          - 2
          - 2.1
        - a3:
          - 3
          - 3.1
          - 3.2
      b:
        - b1: [4, 4.1, 4.2, 4.3]
        - b2: [5, 5.1, 5.2, 5.3, 5.4]
        - b3: [6, 6.1, 6.2, 6.3, 6.4, 6.5]
"""
    complex: dict[str, list[dict[str, list[float]]]] = {
        "a": [
            {"a1": [1]},
            {"a2": [2, 2.1]},
            {"a3": [3, 3.1, 3.2]},
        ],
        "b": [
            {"b1": [4, 4.1, 4.2, 4.3]},
            {"b2": [5, 5.1, 5.2, 5.3, 5.4]},
            {"b3": [6, 6.1, 6.2, 6.3, 6.4, 6.5]},
        ],
    }
    yaml_cfg = yaml.safe_load(yaml_str)
    vset: VariantSet = parser.parse([yaml_cfg])

    assert len(vset.variants) == 1
    assert vset.names == {"variant1"}

    for variant in vset.variants:
        assert all(isinstance(b, Binding) for b in variant.bindings)
        assert variant.names == {"complex"}

    v = next(v for v in vset.variants if v.name == "variant1")
    values = [b.value for b in v.bindings]
    assert values == [complex]

    
def test_multiple_implicit_variants_no_name_multiple_yaml(settings):
    parser = VariantParser(settings)
    yaml_str1 = """
variants:
  param1: 1
"""
    yaml_str2 = """
variants:
  param1: 2
"""
    yaml_cfg1 = yaml.safe_load(yaml_str1)
    yaml_cfg2 = yaml.safe_load(yaml_str2)
    vset: VariantSet = parser.parse([yaml_cfg1, yaml_cfg2])

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

def test_multiple_implicit_variants_with_name_multiple_yaml(settings):
    parser = VariantParser(settings)
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
    yaml_cfg1 = yaml.safe_load(expl_yaml1_str)
    yaml_cfg2 = yaml.safe_load(expl_yaml2_str)
    vset: VariantSet = parser.parse([yaml_cfg1, yaml_cfg2])

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

def test_implicit_variants_mixed_name(settings):
    parser = VariantParser(settings)
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
    yaml_cfg1 = yaml.safe_load(impl_yaml_str)
    yaml_cfg2 = yaml.safe_load(expl_yaml_str)
    vset: VariantSet = parser.parse([yaml_cfg1, yaml_cfg2])

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
# Explicit variant tests
# -----------------------------

def test_single_explicit_variant(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
variants:
  name: variant1
  bindings:
    param1: 42
    param2: "abc"
""")
    vset: VariantSet = parser.parse([yaml_cfg])

    assert len(vset.variants) == 1
    variant = vset.variants[0]
    assert variant.name == "variant1"
    assert variant.names == {"param1", "param2"}

    b1 = variant.get("param1")
    b2 = variant.get("param2")
    assert b1 is not None and b1.value == 42 and b1.index == 0
    assert b2 is not None and b2.value == "abc" and b2.index == 1

def test_explicit_variant_complex_object(settings):
    parser = VariantParser(settings)
    yaml_str = """
variants:
  name: variant1
  bindings:
    complex: 
      a:
        - a1:
          - 1
        - a2:
          - 2
          - 2.1
        - a3:
          - 3
          - 3.1
          - 3.2
      b:
        - b1: [4, 4.1, 4.2, 4.3]
        - b2: [5, 5.1, 5.2, 5.3, 5.4]
        - b3: [6, 6.1, 6.2, 6.3, 6.4, 6.5]
"""
    complex: dict[str, list[dict[str, list[float]]]] = {
        "a": [
            {"a1": [1]},
            {"a2": [2, 2.1]},
            {"a3": [3, 3.1, 3.2]},
        ],
        "b": [
            {"b1": [4, 4.1, 4.2, 4.3]},
            {"b2": [5, 5.1, 5.2, 5.3, 5.4]},
            {"b3": [6, 6.1, 6.2, 6.3, 6.4, 6.5]},
        ],
    }
    yaml_cfg = yaml.safe_load(yaml_str)
    vset: VariantSet = parser.parse([yaml_cfg])

    assert len(vset.variants) == 1
    assert vset.names == {"variant1"}

    for variant in vset.variants:
        assert all(isinstance(b, Binding) for b in variant.bindings)
        assert variant.names == {"complex"}

    v = next(v for v in vset.variants if v.name == "variant1")
    values = [b.value for b in v.bindings]
    assert values == [complex]

def test_multiple_explicit_variants_one_yaml(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
variants:
  - name: variant1
    bindings:
      param1: 1
      param2: "a"
  - name: variant2
    bindings:
      param1: 2
      param2: "b"
  - name: variant3
    bindings:
      param1:
        - 1
        - 2
        - 3
      param2: "c"
""")
    vset: VariantSet = parser.parse([yaml_cfg])

    assert len(vset.variants) == 3
    assert vset.names == {"variant1", "variant2", "variant3"}

    for variant in vset.variants:
        assert all(isinstance(b, Binding) for b in variant.bindings)
        assert variant.names == {"param1", "param2"}

    v3 = next(v for v in vset.variants if v.name == "variant3")
    values = [b.value for b in v3.bindings]
    assert values == [[1, 2, 3], "c"]

def test_multiple_explicit_variants_multiple_yaml_1(settings):
    parser = VariantParser(settings)
    yaml_cfg1 = safe_load("""
variants:
  - name: variant1
    bindings:
      param1: 1
  - name: variant2
    bindings:
      param1: 2
""")
    yaml_cfg2 = safe_load("""
variants:
  name: variant3
  bindings:
    param1: 3
""")
    vset: VariantSet = parser.parse([yaml_cfg1, yaml_cfg2])

    assert vset.names == {"variant1", "variant2", "variant3"}
    v1 = next(v for v in vset.variants if v.name == "variant1")
    v2 = next(v for v in vset.variants if v.name == "variant2")
    v3 = next(v for v in vset.variants if v.name == "variant3")
    b1 = v1.get("param1")
    assert b1 is not None and b1.value == 1
    b2 = v2.get("param1")
    assert b2 is not None and b2.value == 2
    b3 = v3.get("param1")
    assert b3 is not None and b3.value == 3

def test_multiple_explicit_variants_multiple_yaml_2(settings):
    parser = VariantParser(settings)
    yaml_cfg1 = safe_load("""
variants:
  - name: variant1
    bindings:
      param1: 1
""")
    yaml_cfg2 = safe_load("""
variants:
  name: variant2
  bindings:
    param1: 2
""")
    yaml_cfg3 = safe_load("""
variants:
  name: variant3
  bindings:
    param1: 3
""")
    vset: VariantSet = parser.parse([yaml_cfg1, yaml_cfg2, yaml_cfg3])

    assert vset.names == {"variant1", "variant2", "variant3"}
    v1 = next(v for v in vset.variants if v.name == "variant1")
    v2 = next(v for v in vset.variants if v.name == "variant2")
    v3 = next(v for v in vset.variants if v.name == "variant3")
    b1 = v1.get("param1")
    assert b1 is not None and b1.value == 1
    b2 = v2.get("param1")
    assert b2 is not None and b2.value == 2
    b3 = v3.get("param1")
    assert b3 is not None and b3.value == 3

# -----------------------------
# Mixed explicit and implicit variants
# -----------------------------

def test_explicit_and_implicit_variants(settings):
    parser = VariantParser(settings)

    impl_no_name_yaml = safe_load("""
variants:
  param1: 100
  param2: foo
""")
    impl_name_yaml = safe_load("""
variants:
  implicit1:
    param1: 200
    param2: bar
  implicit2:
    param1: 300
    param2: zet
""")
    expl_yaml = safe_load("""
variants:
  - name: explicit1
    bindings: 
      param1: 400
      param2: har
  - name: explicit2
    bindings:
      param1: 500
      param2: lop
""")
    expl_yaml_single = safe_load("""
variants:
  name: explicit3
  bindings: 
    param1: 600
    param2: sot
""")

    # Parse all variant configs as a list of dicts
    vset: VariantSet = parser.parse([impl_no_name_yaml, impl_name_yaml, expl_yaml, expl_yaml_single])

    # All variant names should be present
    expected_names = {"default_1", "implicit1", "implicit2", "explicit1", "explicit2", "explicit3"}
    assert vset.names == expected_names

    # Check implicit no-name variant
    default_variant = next(v for v in vset.variants if v.name == "default_1")
    b1 = default_variant.get("param1")
    b2 = default_variant.get("param2")
    assert b1 is not None
    assert b2 is not None
    assert b1.value == 100
    assert b2.value == "foo"

    # Check implicit named variants
    implicit1 = next(v for v in vset.variants if v.name == "implicit1")
    b1 = implicit1.get("param1")
    b2 = implicit1.get("param2")
    assert b1 is not None
    assert b2 is not None
    assert b1.value == 200
    assert b2.value == "bar"

    implicit2 = next(v for v in vset.variants if v.name == "implicit2")
    b1 = implicit2.get("param1")
    b2 = implicit2.get("param2")
    assert b1 is not None
    assert b2 is not None
    assert b1.value == 300
    assert b2.value == "zet"

    # Check explicit variants
    explicit1 = next(v for v in vset.variants if v.name == "explicit1")
    b1 = explicit1.get("param1")
    b2 = explicit1.get("param2")
    assert b1 is not None
    assert b2 is not None
    assert b1.value == 400
    assert b2.value == "har"

    explicit2 = next(v for v in vset.variants if v.name == "explicit2")
    b1 = explicit2.get("param1")
    b2 = explicit2.get("param2")
    assert b1 is not None
    assert b2 is not None
    assert b1.value == 500
    assert b2.value == "lop"

    explicit3 = next(v for v in vset.variants if v.name == "explicit3")
    b1 = explicit3.get("param1")
    b2 = explicit3.get("param2")
    assert b1 is not None
    assert b2 is not None
    assert b1.value == 600
    assert b2.value == "sot"


# -----------------------------
# Duplicate variant names
# -----------------------------

def test_implicit_duplicate_variant_name_raises(settings):
    parser = VariantParser(settings)
    yaml_expl1 = safe_load("""
variants:
  variant1:
    a: 1
""")
    yaml_expl2 = safe_load("""
variants:
  variant1:
    a: 2
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_expl1, yaml_expl2])

def test_explicit_duplicate_variant_name_raises_1(settings):
    parser = VariantParser(settings)
    yaml_expl1 = safe_load("""
variants:
  name: variant1
  bindings:
    a: 1
""")
    yaml_expl2 = safe_load("""
variants:
  name: variant1
  bindings:
    a: 2
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_expl1, yaml_expl2])

def test_explicit_duplicate_variant_name_raises_2(settings):
    parser = VariantParser(settings)
    yaml_expl1 = safe_load("""
variants:
  - name: variant1
    bindings:
      a: 1
  - name: variant2
    bindings:
      a: 2
""")
    yaml_expl2 = safe_load("""
variants:
  name: variant2
  bindings:
    a: 3
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_expl1, yaml_expl2])

def test_explicit_duplicate_variant_name_raises_3(settings):
    parser = VariantParser(settings)
    yaml_expl1 = safe_load("""
variants:
  - name: variant1
    bindings:
      a: 1
  - name: variant3
    bindings:
      a: 2
""")
    yaml_expl2 = safe_load("""
variants:
  - name: variant2
    bindings:
      a: 3
  - name: variant3
    bindings:
      a: 4
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_expl1, yaml_expl2])

def test_mixed_duplicate_variant_name_raises_1(settings):
    parser = VariantParser(settings)
    yaml_expl = safe_load("""
variants:
  - name: variant1
    bindings:
      a: 1
  - name: variant2
    bindings:
      a: 2
""")
    yaml_impl = safe_load("""
variants:
  variant2:
    a: 3
  variant3:
    a: 4
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_expl, yaml_impl])

def test_mixed_duplicate_variant_name_raises_2(settings):
    parser = VariantParser(settings)
    yaml_expl = safe_load("""
variants:
  name: variant1
  bindings:
    a: 1
""")
    yaml_impl = safe_load("""
variants:
  variant2:
    a: 3
  variant1:
    a: 4
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_expl, yaml_impl])


# -----------------------------
# Missing top-level variants key
# -----------------------------

def test_implicit_without_name_missing_variants_key_yaml(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
wrong_key:
  param1: 1
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_cfg])

def test_implicit_with_name_missing_variants_key_yaml(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
wrong_key:
  variant1:
    param1: 1
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_cfg])

def test_explicit_single_missing_variants_key_yaml(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
wrong_key:
  name: variant1
  bindings:
    param1: 1
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_cfg])

def test_explicit_multiple_missing_variants_key_yaml(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
wrong_key:
  - name: variant1
    bindings:
      param1: 1
""")
    with pytest.raises(IllegalVariantError):
        parser.parse([yaml_cfg])


# -----------------------------
# Binding indices
# -----------------------------

def test_implicit_without_name_yaml_binding_indices(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
variants:
  paramA: 10
  paramB: 20
""")
    vset: VariantSet = parser.parse([yaml_cfg])
    variant = vset.variants[0]

    b_a = variant.get("paramA")
    b_b = variant.get("paramB")
    assert b_a is not None
    assert b_b is not None
    assert b_a.index == 0
    assert b_b.index == 1

def test_implicit_with_name_yaml_binding_indices(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
variants:
  variant1:
    paramA: 10
    paramB: 20
""")
    vset: VariantSet = parser.parse([yaml_cfg])
    variant = vset.variants[0]

    b_a = variant.get("paramA")
    b_b = variant.get("paramB")
    assert b_a is not None
    assert b_b is not None
    assert b_a.index == 0
    assert b_b.index == 1

def test_explicit_single_yaml_binding_indices(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
variants:
  name: variant1
  bindings:
    paramA: 10
    paramB: 20
""")
    vset: VariantSet = parser.parse([yaml_cfg])
    variant = vset.variants[0]

    b_a = variant.get("paramA")
    b_b = variant.get("paramB")
    assert b_a is not None
    assert b_b is not None
    assert b_a.index == 0
    assert b_b.index == 1

def test_explicit_multiple_yaml_binding_indices(settings):
    parser = VariantParser(settings)
    yaml_cfg = safe_load("""
variants:
  - name: variant1
    bindings:
      paramA: 10
      paramB: 20
""")
    vset: VariantSet = parser.parse([yaml_cfg])
    variant = vset.variants[0]

    b_a = variant.get("paramA")
    b_b = variant.get("paramB")
    assert b_a is not None
    assert b_b is not None
    assert b_a.index == 0
    assert b_b.index == 1


