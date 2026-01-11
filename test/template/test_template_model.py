import pytest
from pydantic import BaseModel
from typing import Any
from types import SimpleNamespace
from templisafe.template.template_model import (
    Outcome,
    Diagnostic,
    Schema,
    Template,
    CompilationSpec,
    Compilation,
    Binding,
    Variant,
    VariantSet,
    Parameterization,
    RenderingSpec,
    Rendering,
    Build,
)
from templisafe.exceptions.var_error import MissingVarError
from templisafe.exceptions.binding_error import MissingBindingError
from templisafe.exceptions.parameterization_error import MissingParameterizationError
from templisafe.exceptions.compilation_error import CompilationFailureError
from templisafe.exceptions.rendering_error import RenderingFailureError


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
# QBinding & QVariant Tests
# ========================

def test_qbinding():
    b = Binding(index=0, name="x", value=10)
    assert b.index == 0
    assert b.name == "x"
    assert b.value == 10


def test_qvariant_basic():
    bindings = [Binding(0, "a", 1), Binding(1, "b", "x")]
    v = Variant("var1", bindings)
    assert v.name == "var1"
    assert set(v.mapping.keys()) == {"a", "b"}
    assert v.names == {"a", "b"}
    assert len(v.bindings) == 2
    assert v["a"].value == 1
    assert "b" in v
    with pytest.raises(MissingBindingError):
        _ = v["c"]
    with pytest.raises(MissingBindingError):
        del v["c"]
    del v["a"]
    assert "a" not in v


def test_qvariantset():
    v1 = Variant("v1", [Binding(0, "a", 1)])
    v2 = Variant("v2", [Binding(0, "a", 2)])
    vset = VariantSet([v1, v2])
    assert vset.names == {"v1", "v2"}
    assert len(vset.variants) == 2


# ========================
# QRenderingSpec Tests
# ========================

def test_qrenderingspec_basic():
    v1 = Variant("v1", [Binding(0, "a", 1)])
    p1 = Parameterization(v1, "rendered1")
    spec = RenderingSpec([p1])
    assert spec.names == {"v1"}
    assert spec["v1"].rendered_str == "rendered1"
    assert list(spec) == [p1]
    assert spec.get("v1") == p1
    assert spec.get("missing") is None
    with pytest.raises(MissingParameterizationError):
        _ = spec["missing"]
    with pytest.raises(MissingParameterizationError):
        del spec["missing"]


def test_qrenderingspec_mapping_independence():
    v1 = Variant("v1", [Binding(0, "a", 1)])
    p1 = Parameterization(v1, "rendered1")
    spec = RenderingSpec([p1])
    mapping_copy: dict[str, Any] = spec.mapping
    mapping_copy["v1"] = "tampered"
    # Original spec unchanged
    assert isinstance(spec["v1"], Parameterization)


# ========================
# QCompilation & QRendering Tests
# ========================

def test_qcompilation_access(compiled):
    assert compiled.compiled is not None
    empty_comp = Compilation(Outcome.ERROR, "fail")
    with pytest.raises(CompilationFailureError):
        _ = empty_comp.compiled


def test_qrendering_access():
    v1 = Variant("v1", [Binding(0, "a", 1)])
    p1 = Parameterization(v1, "rendered")
    spec = RenderingSpec([p1])
    rendering = Rendering(Outcome.SUCCESS, "ok", _spec=spec)
    assert rendering.rendered == spec

    empty_rendering = Rendering(Outcome.ERROR, "fail")
    with pytest.raises(RenderingFailureError):
        _ = empty_rendering.rendered


# ========================
# QBuild Tests
# ========================

def test_qbuild_outcome():
    v1 = Variant("v1", [Binding(0, "a", 1)])
    p1 = Parameterization(v1, "rendered")
    spec = RenderingSpec([p1])
    rendering = Rendering(Outcome.WARNING, "warn", _spec=spec)
    template = Template(template_str="{{ a }}", vars={"a"})
    schema = Schema(model_cls=BaseModel)
    comp_spec = CompilationSpec(template, schema)
    compilation = Compilation(Outcome.SUCCESS, "ok", _spec=comp_spec)
    build = Build(compilation, rendering)
    # max of compilation (SUCCESS=0) and rendering (WARNING=1) => WARNING
    assert build.outcome == Outcome.WARNING
