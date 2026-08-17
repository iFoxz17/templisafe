import pytest
from pydantic import BaseModel

from templisafe.exceptions.binding_error import MissingBindingError
from templisafe.exceptions.compilation_error import CompilationFailureError
from templisafe.exceptions.parameterization_error import MissingParameterizationError
from templisafe.exceptions.rendering_error import RenderingFailureError
from templisafe.template.template_model import (
    Binding,
    Build,
    Compilation,
    CompilationSpec,
    Diagnostic,
    Outcome,
    Parameterization,
    Rendering,
    RenderingSpec,
    Schema,
    Template,
    Variant,
    VariantSet,
)

# ========================
# Fixtures
# ========================


@pytest.fixture
def schema_model():
    class TestModel(BaseModel):
        a: int
        b: str

    return Schema(model_cls=TestModel)


@pytest.fixture
def compiled(schema_model):
    template = Template(template_str="{{ a }} {{ b }}", vars={"a", "b"})
    spec = CompilationSpec(template=template, schema=schema_model)
    return Compilation(outcome=Outcome.SUCCESS, message="ok", _spec=spec)


# ========================
# Diagnostic Tests
# ========================


def test_diagnostic_creation():
    diag = Diagnostic(level=Outcome.WARNING, message="Check variable", name="x", index=0)
    assert diag.level == Outcome.WARNING
    assert diag.message == "Check variable"
    assert diag.name == "x"
    assert diag.index == 0

    diag = Diagnostic(level=Outcome.WARNING, message="Check variable")
    assert diag.level == Outcome.WARNING
    assert diag.message == "Check variable"
    assert diag.name is None
    assert diag.index is None


# ========================
# Schema Tests
# ========================


def test_schema_model_class(schema_model: Schema):
    assert schema_model.model_cls.__name__ == "TestModel"


# ========================
# Template Tests
# ========================


def test_template_properties():
    t = Template(template_str="{{ a }}", vars={"a"})
    assert t.template_str == "{{ a }}"
    assert t.vars == {"a"}


# ========================
# CompilationSpec Tests
# ========================


def test_compilation_spec_attributes(schema_model):
    t = Template(template_str="{{ a }}", vars={"a"})
    spec = CompilationSpec(template=t, schema=schema_model)
    assert spec.template is t
    assert spec.schema is schema_model


# ========================
# Binding & Variant Tests
# ========================


def test_binding_basic():
    b = Binding(index=0, name="x", value=10)
    assert b.index == 0
    assert b.name == "x"
    assert b.value == 10


def test_variant_operations():
    b1 = Binding(0, "a", 1)
    b2 = Binding(1, "b", "x")
    v = Variant("var1", [b1, b2])

    assert v.name == "var1"
    assert set(v.mapping.keys()) == {"a", "b"}
    assert v.names == {"a", "b"}
    assert len(v.bindings) == 2
    assert v["a"].value == 1
    with pytest.raises(TypeError):
        del v["a"]
    assert "a" in v
    with pytest.raises(MissingBindingError):
        _ = v["c"]
    mapping_copy = v.mapping
    mapping_copy["a"] = Binding(0, "a", 999)
    assert v["a"].value == 1


def test_variant_set_collection():
    v1 = Variant("v1", [Binding(0, "a", 1)])
    v2 = Variant("v2", [Binding(0, "a", 2)])
    vset = VariantSet([v1, v2])
    assert vset.names == {"v1", "v2"}
    assert len(vset.variants) == 2
    assert isinstance(vset.variants, tuple)


# ========================
# Parameterization & RenderingSpec
# ========================


def test_parameterization_properties():
    v = Variant("v1", [Binding(0, "a", 1)])
    p = Parameterization(v, "rendered1")
    assert p.variant is v
    assert p.rendered_str == "rendered1"


def test_rendering_spec_operations():
    v = Variant("v1", [Binding(0, "a", 1)])
    p = Parameterization(v, "rendered1")
    spec = RenderingSpec([p])

    assert spec.names == {"v1"}
    assert spec["v1"] is p
    assert spec.get("missing") is None
    with pytest.raises(MissingParameterizationError):
        _ = spec["missing"]
    mapping_copy = spec.mapping
    mapping_copy["v1"] = "tampered"  # type: ignore
    assert spec["v1"] is p  # Original remains intact


# ========================
# Compilation & Rendering
# ========================


def test_compilation_access(compiled: Compilation):
    assert compiled.compiled is not None
    empty = Compilation(Outcome.ERROR, "fail")
    with pytest.raises(CompilationFailureError):
        _ = empty.compiled


def test_rendering_access():
    v = Variant("v1", [Binding(0, "a", 1)])
    p = Parameterization(v, "rendered")
    spec = RenderingSpec([p])
    rendering = Rendering(Outcome.SUCCESS, "ok", _spec=spec)
    assert rendering.rendered is spec

    empty_rendering = Rendering(Outcome.ERROR, "fail")
    with pytest.raises(RenderingFailureError):
        _ = empty_rendering.rendered


# ========================
# Build Tests
# ========================


def test_build_outcome_priority():
    v = Variant("v1", [Binding(0, "a", 1)])
    p = Parameterization(v, "rendered")
    spec = RenderingSpec([p])

    rendering = Rendering(Outcome.WARNING, "warn", _spec=spec)
    template = Template(template_str="{{ a }}", vars={"a"})
    schema = Schema(BaseModel)
    comp_spec = CompilationSpec(template, schema)
    compilation = Compilation(Outcome.SUCCESS, "ok", _spec=comp_spec)
    build = Build(compilation, rendering)

    # Outcome should be max of compilation and rendering
    assert build.outcome == Outcome.WARNING


def test_build_error_outcome_dominates():
    v = Variant("v1", [Binding(0, "a", 1)])
    p = Parameterization(v, "rendered")
    spec = RenderingSpec([p])

    rendering = Rendering(Outcome.ERROR, "fail", _spec=spec)
    template = Template(template_str="{{ a }}", vars={"a"})
    schema = Schema(BaseModel)
    comp_spec = CompilationSpec(template, schema)
    compilation = Compilation(Outcome.WARNING, "warn", _spec=comp_spec)
    build = Build(compilation, rendering)

    assert build.outcome == Outcome.ERROR
