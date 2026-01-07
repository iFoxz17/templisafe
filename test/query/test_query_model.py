import pytest
from sqltemplater.util.util import DiagnosticPolicy, ContentType
from sqltemplater.query.query_model import (
    QVar,
    QSchema,
    QTemplate,
    QCompilationSpec,
    QBinding,
    QVariant,
    QRenderingSpec
)
from sqltemplater.exceptions.var_error import MissingVarError

# -----------------------
# DiagnosticPolicy & ContentType
# -----------------------
def test_diagnostic_policy_enum():
    assert DiagnosticPolicy.ERRORS_ONLY.value == 0
    assert DiagnosticPolicy.LOG_WARNINGS.value == 1
    assert DiagnosticPolicy.RAISE_WARNINGS.value == 2


def test_content_type_enum():
    assert ContentType.YAML.value == "yaml"
    assert ContentType.JINJA.value == "j2"


# -----------------------
# ParamSchema
# -----------------------
def test_param_schema_frozen():
    p = QVar(index=0, name="param", type_=int, default=5)
    assert p.index == 0
    with pytest.raises(AttributeError):
        p.index = 1  # type: ignore


# -----------------------
# QuerySchema
# -----------------------
def test_query_schema_basic():
    p1 = QVar(0, "a", int, 1)
    p2 = QVar(1, "b", str, "x")
    schema = QSchema([p1, p2])

    # Test names and params
    assert schema.names == {"a", "b"}
    assert set(schema.vars) == {p1, p2}

    # Test param lookup
    assert schema.get("a") == p1
    assert schema.get("missing", default=p2) == p2
    assert schema["a"] == p1
    assert "a" in schema
    assert "missing" not in schema

    # Test add_param
    p3 = QVar(2, "c", float)
    schema.add_param(p3)
    assert schema.get("c") == p3

    # Test delete
    del schema["c"]
    assert "c" not in schema
    with pytest.raises(MissingVarError):
        del schema["c"]
    with pytest.raises(MissingVarError):
        _ = schema["c"]

    # Test iteration
    names = [p.name for p in schema]
    assert set(names) == {"a", "b"}


def test_query_schema_repr():
    p1 = QVar(0, "a", int)
    schema = QSchema([p1])
    r = repr(schema)
    assert "QuerySchema" in r
    assert "a" in r


# -----------------------
# QueryTemplate
# -----------------------
def test_query_template():
    tmpl = QTemplate(template="SELECT * FROM table", vars={"a", "b"})
    assert tmpl.template == "SELECT * FROM table"
    assert tmpl.vars == {"a", "b"}
    assert "QueryTemplate" in repr(tmpl)


# -----------------------
# CompiledQuery
# -----------------------
def test_compiled_query():
    tmpl = QTemplate(template="SELECT *", vars=set())
    schema = QSchema()
    cq = QCompilationSpec(template=tmpl, schema=schema)
    assert cq.template == tmpl
    assert cq.schema == schema


# -----------------------
# QueryParams
# -----------------------
def test_query_params():
    qp = QVariant(bindings=[
        QBinding(index=0, name="a", value=1),
        QBinding(index=1, name="b", value=2),
    ])

    assert len(qp.binding_by_name) == 2
    assert qp.binding_by_name[0].index == 0
    assert qp.binding_by_name[0].name == "a"
    assert qp.binding_by_name[0].value == 1


# -----------------------
# RenderedQuery
# -----------------------
def test_rendered_query():
    tmpl = QTemplate(template="SELECT *", vars=set())
    schema = QSchema()
    cq = QCompilationSpec(template=tmpl, schema=schema)
    qp = QVariant(bindings=[
        QBinding(index=0, name="x", value=1)
    ])

    rq = QRenderingSpec(compiled=cq, params=qp, rendered="SELECT *")
    assert rq.compiled == cq
    assert rq.params == qp
    assert rq.rendered == "SELECT *"
