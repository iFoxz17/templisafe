from typing import Annotated, Any, Optional

import pytest
from pydantic import Field, create_model

from templisafe.core.metadata import Metadata, MetaValue
from templisafe.engine.jinja_template_engine import JinjaTemplateEngine
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.template.renderer.renderer import Renderer
from templisafe.template.template_model import (
    Binding,
    CompilationSpec,
    Outcome,
    Schema,
    Template,
    Variant,
    VariantSet,
)

# ========================
# Fixtures
# ========================


@pytest.fixture
def renderer_settings() -> RendererSettings:
    return RendererSettings(index_key="_index")


@pytest.fixture
def engine() -> JinjaTemplateEngine:
    settings = TemplateEngineSettings.create(engine_kind="jinja", config={})
    return JinjaTemplateEngine(settings)


def indexed(annotation: Any, index: int) -> Any:
    return Annotated[annotation, Metadata({"_index": MetaValue(index)})]


@pytest.fixture
def schema_model():
    fields: dict[str, Any] = {
        "a": (indexed(int, 0), Field(default=1)),
        "b": (indexed(str, 1), Field(default="default")),
        "c": (indexed(float, 2), Field(...)),
    }
    return Schema(model_cls=create_model("TestSchema", **fields))


@pytest.fixture
def compilation(schema_model):
    return CompilationSpec(
        template=Template("{{ a }} {{ b }} {{ c }}", vars={"a", "b", "c"}),
        schema=schema_model,
    )


# ========================
# Tests
# ========================


# -----------------------------
# Basic rendering success
# -----------------------------
def test_render_success(engine, compilation, renderer_settings: RendererSettings):
    renderer = Renderer(renderer_settings)
    bindings = [Binding(0, "a", 10), Binding(1, "b", "hello"), Binding(2, "c", 1.5)]
    vset = VariantSet([Variant("default", bindings)])

    rendered = renderer.render(compilation, vset, engine)

    assert rendered.outcome == Outcome.SUCCESS
    assert rendered.rendered.parameterizations[0].rendered_str == "10 hello 1.5"


def test_render_missing_binding_with_default(engine, compilation, renderer_settings):
    renderer = Renderer(renderer_settings)
    bindings = [Binding(0, "a", 10), Binding(2, "c", 2.5)]
    vset = VariantSet([Variant("default", bindings)])

    rendered = renderer.render(compilation, vset, engine)

    assert rendered.outcome == Outcome.SUCCESS
    assert "default" in rendered.rendered.parameterizations[0].rendered_str


def test_render_optional_values(engine, renderer_settings):
    fields: dict[str, Any] = {
        "x": (indexed(int | None, 0), Field(default=None)),
        "y": (indexed(Optional[str], 1), Field(default=None)),
    }
    schema = Schema(model_cls=create_model("OptionalSchema", **fields))
    compilation = CompilationSpec(template=Template("{{ x }} {{ y }}", vars={"x", "y"}), schema=schema)

    renderer = Renderer(renderer_settings)
    bindings = [Binding(0, "x", 42), Binding(1, "y", None)]
    vset = VariantSet([Variant("default", bindings)])
    rendered = renderer.render(compilation, vset, engine)

    assert rendered.outcome == Outcome.SUCCESS
    assert "42" in rendered.rendered.parameterizations[0].rendered_str
    assert "None" in rendered.rendered.parameterizations[0].rendered_str


def test_render_missing_optional_null_default(engine, renderer_settings):
    fields: dict[str, Any] = {
        "x": (indexed(int, 0), Field(...)),
        "y": (indexed(Optional[str], 1), Field(default=None)),
    }
    schema = Schema(model_cls=create_model("OptionalDefaultSchema", **fields))
    compilation = CompilationSpec(template=Template("{{ x }} {{ y }}", vars={"x", "y"}), schema=schema)

    renderer = Renderer(renderer_settings)
    bindings = [Binding(0, "x", 42)]
    vset = VariantSet([Variant("default", bindings)])
    rendered = renderer.render(compilation, vset, engine)

    assert rendered.outcome == Outcome.SUCCESS
    assert rendered.rendered.parameterizations[0].rendered_str == "42 None"


def test_render_nested_list_variable(engine, renderer_settings):
    fields: dict[str, Any] = {"matrix": (indexed(list[list[float]], 0), Field(...))}
    schema = Schema(model_cls=create_model("NestedSchema", **fields))
    compilation = CompilationSpec(template=Template("{{ matrix }}", vars={"matrix"}), schema=schema)

    renderer = Renderer(renderer_settings)
    bindings = [Binding(0, "matrix", [[1.1, 2], [3, 4.4]])]
    vset = VariantSet([Variant("default", bindings)])
    rendered = renderer.render(compilation, vset, engine)

    assert rendered.outcome == Outcome.SUCCESS
    assert "[[1.1, 2], [3, 4.4]]" in rendered.rendered.parameterizations[0].rendered_str


def test_render_complex_object_variable(engine, renderer_settings):
    fields: dict[str, Any] = {
        "complex": (
            indexed(dict[str, list[dict[str, list[float]]]], 0),
            Field(...),
        )
    }
    schema = Schema(model_cls=create_model("NestedSchema", **fields))
    compilation = CompilationSpec(template=Template("{{ complex }}", vars={"complex"}), schema=schema)

    object: dict[str, list[dict[str, list[float]]]] = {
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
    renderer = Renderer(renderer_settings)
    bindings = [Binding(0, "complex", object)]
    vset = VariantSet([Variant("default", bindings)])
    rendered = renderer.render(compilation, vset, engine)

    assert rendered.outcome == Outcome.SUCCESS
    assert str(object) in rendered.rendered.parameterizations[0].rendered_str


# -----------------------------
# Extra / wrong / missing bindings
# -----------------------------
def test_render_extra_binding(engine, compilation, renderer_settings):
    renderer = Renderer(renderer_settings)
    bindings = [
        Binding(0, "a", 10),
        Binding(1, "b", "hello"),
        Binding(2, "c", 3.0),
        Binding(3, "x", "extra"),
    ]
    vset = VariantSet([Variant("default", bindings)])
    rendered = renderer.render(compilation, vset, engine)

    assert rendered.outcome == Outcome.WARNING
    assert any("Extra binding" in d.message for d in rendered.diagnostics)


def test_render_missing_required_binding(engine, compilation, renderer_settings):
    renderer = Renderer(renderer_settings)
    bindings = [Binding(0, "a", 10), Binding(1, "b", "hello")]  # missing required 'c'
    vset = VariantSet([Variant("default", bindings)])
    rendered = renderer.render(compilation, vset, engine)

    assert rendered.outcome == Outcome.ERROR
    assert any("Missing required binding" in d.message for d in rendered.diagnostics)


def test_render_wrong_type_binding(engine, compilation, renderer_settings):
    renderer = Renderer(renderer_settings)
    bindings = [
        Binding(0, "a", "wrong"),
        Binding(1, "b", "hello"),
        Binding(2, "c", 1.0),
    ]
    vset = VariantSet([Variant("default", bindings)])
    rendered = renderer.render(compilation, vset, engine)

    assert rendered.outcome == Outcome.ERROR
    assert any("Invalid value" in d.message for d in rendered.diagnostics)


# -----------------------------
# Multiple variants
# -----------------------------
def test_render_multiple_variants(engine, compilation, renderer_settings):
    renderer = Renderer(renderer_settings)
    variant1 = Variant("Var1", [Binding(0, "a", 1), Binding(1, "b", "x"), Binding(2, "c", 1.1)])
    variant2 = Variant("Var2", [Binding(0, "a", 2), Binding(1, "b", "y"), Binding(2, "c", 2.2)])
    vset = VariantSet([variant1, variant2])

    rendered = renderer.render(compilation, vset, engine)
    texts = [p.rendered_str for p in rendered.rendered.parameterizations]
    assert "1" in texts[0] and "x" in texts[0] and "1.1" in texts[0]
    assert "2" in texts[1] and "y" in texts[1] and "2.2" in texts[1]
    assert rendered.outcome == Outcome.SUCCESS
