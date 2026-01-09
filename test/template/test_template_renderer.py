import pytest
from typing import Any, Optional
from pydantic import Field, create_model
from jinja2 import Environment

from sqltemplater.template.template_model import (
    CompilationSpec,
    Schema,
    Binding,
    Variant,
    VariantSet,
    Template,
    Outcome,
)
from sqltemplater.template.template_renderer import TemplateRenderer


@pytest.fixture
def env():
    return Environment()


@pytest.fixture
def schema_model():
    """
    Schema with:
      - a: int, default
      - b: str, default
      - c: float, NO default (required)
    """
    fields: dict[str, Any] = {
        "a": (int, Field(default=1, json_schema_extra={"_index": 0})),
        "b": (str, Field(default="default", json_schema_extra={"_index": 1})),
        "c": (float, Field(..., json_schema_extra={"_index": 2})),
    }
    model_cls = create_model("TestSchema", **fields)
    return Schema(model_cls=model_cls)


@pytest.fixture
def compilation(schema_model):
    return CompilationSpec(
        template=Template(
            template="{{ a }} {{ b }} {{ c }}",
            vars={"a", "b", "c"},
        ),
        schema=schema_model,
    )


def test_render_success(env, compilation):
    renderer = TemplateRenderer(env, index_key="_index")

    bindings = [
        Binding(index=0, name="a", value=10),
        Binding(index=1, name="b", value="hello"),
        Binding(index=2, name="c", value=1.5),
    ]
    variant = Variant("default", bindings)
    vset = VariantSet([variant])

    rendered = renderer.render(compilation, vset)

    assert rendered.outcome == Outcome.SUCCESS
    assert rendered.rendered is not None
    assert rendered.rendered.parameterizations[0].rendered == "10 hello 1.5"
    assert rendered.diagnostics == ()


def test_render_nested_list_variable(env):
    # Schema with nested list[list[float]]
    fields: dict[str, Any] = {
        "matrix": (
            list[list[float]],
            Field(..., json_schema_extra={"_index": 0}),
        ),
    }
    model_cls = create_model("NestedSchema", **fields)
    schema = Schema(model_cls=model_cls)

    compilation = CompilationSpec(
        template=Template(
            template="{{ matrix }}",
            vars={"matrix"},
        ),
        schema=schema,
    )

    renderer = TemplateRenderer(env, index_key="_index")

    bindings = [
        Binding(
            index=0,
            name="matrix",
            value=[[1.1, 2], [3, 4.4]],
        )
    ]
    variant = Variant("default", bindings)
    vset = VariantSet([variant])

    rendered = renderer.render(compilation, vset)

    assert rendered.outcome == Outcome.SUCCESS
    assert rendered.diagnostics == ()
    assert len(rendered.rendered.parameterizations) == 1
    assert rendered.rendered.parameterizations[0].rendered == "[[1.1, 2], [3, 4.4]]"


def test_render_optional_values(env):
    # Schema with optional values
    fields: dict[str, Any] = {
        "x": (
            int | None,
            Field(default=None, json_schema_extra={"_index": 0}),
        ),
        "y": (
            Optional[str],
            Field(default=None, json_schema_extra={"_index": 1}),
        ),
    }
    model_cls = create_model("OptionalSchema", **fields)
    schema = Schema(model_cls=model_cls)

    compilation = CompilationSpec(
        template=Template(
            template="{{ x }} {{ y }}",
            vars={"x", "y"},
        ),
        schema=schema,
    )

    renderer = TemplateRenderer(env, index_key="_index")

    bindings = [
        Binding(index=0, name="x", value=42),   # actual value
        Binding(index=1, name="y", value=None)  # explicit None
    ]
    variant = Variant("default", bindings)
    vset = VariantSet([variant])

    rendered = renderer.render(compilation, vset)

    assert rendered.outcome == Outcome.SUCCESS
    assert rendered.diagnostics == ()
    assert rendered._spec is not None
    assert rendered._spec.parameterizations[0].rendered == "42 None"


def test_render_missing_binding_with_default(env, compilation):
    """Missing 'b' -> allowed because it has a default."""
    renderer = TemplateRenderer(env, index_key="_index")

    bindings = [
        Binding(index=0, name="a", value=10),
        Binding(index=2, name="c", value=2.5),
    ]
    variant = Variant("default", bindings)
    vset = VariantSet([variant])

    rendered = renderer.render(compilation, vset)

    assert rendered.outcome == Outcome.SUCCESS
    rendered_text = rendered.rendered.parameterizations[0].rendered
    assert rendered_text == "10 default 2.5"


def test_render_extra_binding(env, compilation):
    renderer = TemplateRenderer(env, index_key="_index")

    bindings = [
        Binding(index=0, name="a", value=10),
        Binding(index=1, name="b", value="hello"),
        Binding(index=2, name="c", value=3.0),
        Binding(index=3, name="x", value="extra"),
    ]
    variant = Variant("default", bindings)
    vset = VariantSet([variant])

    rendered = renderer.render(compilation, vset)

    assert rendered.outcome == Outcome.WARNING
    diag = rendered.diagnostics[0]
    assert diag.level == Outcome.WARNING
    assert "Extra binding" in diag.message
    assert "'x'" in diag.message
    assert rendered.rendered.parameterizations[0].rendered == "10 hello 3.0"


def test_render_wrong_type_binding(env, compilation):
    renderer = TemplateRenderer(env, index_key="_index")

    bindings = [
        Binding(index=0, name="a", value="not-an-int"),
        Binding(index=1, name="b", value="hello"),
        Binding(index=2, name="c", value=1.0),
    ]
    variant = Variant("default", bindings)
    vset = VariantSet([variant])

    rendered = renderer.render(compilation, vset)

    assert rendered.outcome == Outcome.ERROR
    diag = rendered.diagnostics[0]
    assert diag.level == Outcome.ERROR
    assert "Invalid value" in diag.message
    assert "'a'" in diag.message


def test_render_nested_list_variable_wrong_type(env):
    # Schema with nested list[list[float]]
    fields: dict[str, Any] = {
        "matrix": (
            list[list[float]],
            Field(..., json_schema_extra={"_index": 0}),
        ),
    }
    model_cls = create_model("NestedSchema", **fields)
    schema = Schema(model_cls=model_cls)

    compilation = CompilationSpec(
        template=Template(
            template="{{ matrix }}",
            vars={"matrix"},
        ),
        schema=schema,
    )

    renderer = TemplateRenderer(env, index_key="_index")

    bindings = [
        Binding(
            index=0,
            name="matrix",
            value=[["a", 2.2], [3.3, True]],
        )
    ]
    variant = Variant("default", bindings)
    vset = VariantSet([variant])

    rendered = renderer.render(compilation, vset)

    assert rendered.outcome == Outcome.ERROR
    diag = rendered.diagnostics[0]
    assert diag.level == Outcome.ERROR
    assert "Invalid value" in diag.message
    assert "'matrix'" in diag.message


def test_render_optional_values_wrong_type(env):
    # Schema with optional values
    fields: dict[str, Any] = {
        "x": (
            int | None,
            Field(default=None, json_schema_extra={"_index": 0}),
        ),
        "y": (
            Optional[str],
            Field(default=None, json_schema_extra={"_index": 1}),
        ),
    }
    model_cls = create_model("OptionalSchema", **fields)
    schema = Schema(model_cls=model_cls)

    compilation = CompilationSpec(
        template=Template(
            template="{{ x }} {{ y }}",
            vars={"x", "y"},
        ),
        schema=schema,
    )

    renderer = TemplateRenderer(env, index_key="_index")

    bindings = [
        Binding(index=0, name="x", value="42"),   # Should be an int
        Binding(index=1, name="y", value=42)      # Should be a str
    ]
    variant = Variant("default", bindings)
    vset = VariantSet([variant])

    rendered = renderer.render(compilation, vset)

    assert rendered.outcome == Outcome.ERROR
    assert len(rendered.diagnostics) == 1    
    diag = rendered.diagnostics[0]
    assert diag.level == Outcome.ERROR
    assert "Invalid value" in diag.message
    assert "'x'" in diag.message or "'y'" in diag.message 


def test_render_missing_required_binding(env, compilation):
    renderer = TemplateRenderer(env, index_key="_index")

    # Missing required 'c'
    bindings = [
        Binding(index=0, name="a", value=10),
        Binding(index=1, name="b", value="hello"),
    ]
    variant = Variant("default", bindings)
    vset = VariantSet([variant])

    rendered = renderer.render(compilation, vset)

    assert rendered.outcome == Outcome.ERROR
    diag = rendered.diagnostics[0]
    assert diag.level == Outcome.ERROR
    assert "Missing required binding" in diag.message
    assert "'c'" in diag.message
    assert diag.index == 2


def test_multiple_variants(env, compilation):
    renderer = TemplateRenderer(env, index_key="_index")

    variant1 = Variant(
        "Var1",
        [
            Binding(0, "a", 1),
            Binding(1, "b", "x"),
            Binding(2, "c", 1.1),
        ],
    )
    variant2 = Variant(
        "Var2",
        [
            Binding(0, "a", 2),
            Binding(1, "b", "y"),
            Binding(2, "c", 2.2),
        ],
    )

    vset = VariantSet([variant1, variant2])
    rendering = renderer.render(compilation, vset)

    assert rendering.outcome == Outcome.SUCCESS
    rendered_texts = [p.rendered for p in rendering.rendered.parameterizations]
    assert rendered_texts == ["1 x 1.1", "2 y 2.2"]
