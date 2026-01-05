import pytest
from sqltemplater.query.query_renderer import QueryRenderer, RenderingOutcome
from sqltemplater.query.query_model import (
    QueryTemplate,
    QuerySchema,
    ParamSchema,
    QueryParam,
    QueryParams,
    CompiledQuery
)

# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def simple_template():
    return QueryTemplate(
        template="SELECT * FROM table WHERE id={{ id }} AND name='{{ name }}'",
        params={"id", "name"}
    )


@pytest.fixture
def schema():
    return QuerySchema(params=[
        ParamSchema(index=0, name="id", type_=int),
        ParamSchema(index=1, name="name", type_=str),
    ])


@pytest.fixture
def schema_with_defaults():
    return QuerySchema(params=[
        ParamSchema(index=0, name="id", type_=int, default=0),
        ParamSchema(index=1, name="name", type_=str, default="anonymous"),
    ])


@pytest.fixture
def renderer():
    return QueryRenderer()


# -------------------------
# Success case: all params provided
# -------------------------
def test_render_success(renderer, simple_template, schema):
    compiled = CompiledQuery(template=simple_template, schema=schema)
    params = QueryParams(params=[
        QueryParam(index=0, name="id", value=42),
        QueryParam(index=1, name="name", value="Alice"),
    ])

    result = renderer.render(compiled, params)

    assert result.outcome == RenderingOutcome.SUCCESS
    assert result.rendered_query is not None
    assert "42" in result.rendered_query.query
    assert "Alice" in result.rendered_query.query
    assert result.diagnostics == tuple()


# -------------------------
# Success case: missing params, but schema has defaults
# -------------------------
def test_render_success_with_defaults(renderer, simple_template, schema_with_defaults):
    compiled = CompiledQuery(template=simple_template, schema=schema_with_defaults)
    params = QueryParams(params=[
        QueryParam(index=0, name="id", value=42),  # 'name' missing → default
    ])

    result = renderer.render(compiled, params)

    assert result.outcome == RenderingOutcome.SUCCESS
    assert result.rendered_query is not None
    assert "42" in result.rendered_query.query
    assert "anonymous" in result.rendered_query.query
    assert result.diagnostics == tuple()


# -------------------------
# Warning case: extra parameter
# -------------------------
def test_render_warning_extra_param(renderer, simple_template, schema):
    compiled = CompiledQuery(template=simple_template, schema=schema)
    params = QueryParams(params=[
        QueryParam(index=0, name="id", value=42),
        QueryParam(index=1, name="name", value="Alice"),
        QueryParam(index=2, name="extra", value="foo"),  # extra
    ])

    result = renderer.render(compiled, params)

    assert result.outcome == RenderingOutcome.WARNING
    assert result.rendered_query is not None

    warnings = [d for d in result.diagnostics if d.level == RenderingOutcome.WARNING]
    assert any(d.param == "extra" for d in warnings)


# -------------------------
# Error case: missing parameter without default
# -------------------------
def test_render_error_missing_param(renderer, simple_template, schema):
    compiled = CompiledQuery(template=simple_template, schema=schema)
    params = QueryParams(params=[
        QueryParam(index=0, name="id", value=42),  # missing 'name'
    ])

    result = renderer.render(compiled, params)

    assert result.outcome == RenderingOutcome.ERROR
    assert result.rendered_query is None

    errors = [d for d in result.diagnostics if d.level == RenderingOutcome.ERROR]
    assert any(d.param == "name" for d in errors)


# -------------------------
# Validate method independently
# -------------------------
def test_validate_only(renderer, simple_template, schema):
    compiled = CompiledQuery(template=simple_template, schema=schema)
    params = QueryParams(params=[
        QueryParam(index=0, name="id", value=42),
        QueryParam(index=1, name="name", value="Alice"),
        QueryParam(index=2, name="unused", value="foo"),
    ])

    result = renderer.validate(compiled, params)

    assert result.outcome == RenderingOutcome.WARNING

    warnings = [d for d in result.diagnostics if d.level == RenderingOutcome.WARNING]
    assert any(d.param == "unused" for d in warnings)

    errors = [d for d in result.diagnostics if d.level == RenderingOutcome.ERROR]
    assert not errors
