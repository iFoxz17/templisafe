import pytest
from sqltemplater.query.query_model import QueryTemplate, QuerySchema, ParamSchema, CompiledQuery
from sqltemplater.query.query_compiler import QueryCompiler, CompilationOutcome, CompilationResult, CompilationDiagnostic

# ----------------------------
# Fixtures
# ----------------------------

@pytest.fixture
def compiler() -> QueryCompiler:
    return QueryCompiler()

@pytest.fixture
def template() -> QueryTemplate:
    return QueryTemplate(template="SELECT * FROM table WHERE a = {{a}} AND b = {{b}}", params=set(["a", "b"]))

@pytest.fixture
def matching_schema() -> QuerySchema:
    return QuerySchema(params=[
        ParamSchema(index=0, name="a", type_=int),
        ParamSchema(index=1, name="b", type_=int)
    ])

@pytest.fixture
def schema_with_unused() -> QuerySchema:
    return QuerySchema(params=[
        ParamSchema(index=0, name="a", type_=int),
        ParamSchema(index=1, name="b", type_=int),
        ParamSchema(index=2, name="c", type_=int)
    ])

@pytest.fixture
def schema_with_undeclared() -> QuerySchema:
    return QuerySchema(params=[
        ParamSchema(index=0, name="a", type_=int)
    ])

@pytest.fixture
def schema_with_both_issues() -> QuerySchema:
    return QuerySchema(params=[
        ParamSchema(index=0, name="a", type_=int),
        ParamSchema(index=1, name="c", type_=int)
    ])


# ----------------------------
# Tests
# ----------------------------

def test_compile_without_schema(compiler, template):
    result: CompilationResult = compiler.compile(template)
    assert result.outcome == CompilationOutcome.SUCCESS
    assert result.compiled_query is not None
    assert isinstance(result.compiled_query, CompiledQuery)
    assert result.diagnostics == ()
    assert "without schema" in result.message

def test_compile_with_matching_schema(compiler, template, matching_schema):
    result: CompilationResult = compiler.compile(template, matching_schema)
    assert result.outcome == CompilationOutcome.SUCCESS
    assert result.compiled_query is not None
    assert result.diagnostics == ()
    assert "successfully compiled with schema" in result.message

def test_compile_with_unused_parameter(compiler, template, schema_with_unused):
    result: CompilationResult = compiler.compile(template, schema_with_unused)
    assert result.outcome == CompilationOutcome.WARNING
    assert result.compiled_query is not None
    assert any(d.level == CompilationOutcome.WARNING for d in result.diagnostics)
    assert any("Unused parameter" in d.message for d in result.diagnostics)
    assert any("c" in d.message for d in result.diagnostics)

def test_compile_with_undeclared_parameter(compiler, template, schema_with_undeclared):
    result: CompilationResult = compiler.compile(template, schema_with_undeclared)
    assert result.outcome == CompilationOutcome.ERROR
    assert result.compiled_query is None
    assert any(d.level == CompilationOutcome.ERROR for d in result.diagnostics)
    assert any("Undeclared parameter: 'b'" in d.message for d in result.diagnostics)

def test_compile_with_both_unused_and_undeclared(compiler, template, schema_with_both_issues):
    result: CompilationResult = compiler.compile(template, schema_with_both_issues)
    assert result.outcome == CompilationOutcome.ERROR
    assert result.compiled_query is None
    # Check that both warning and error diagnostics are present
    warning_messages = [d for d in result.diagnostics if d.level == CompilationOutcome.WARNING]
    error_messages = [d for d in result.diagnostics if d.level == CompilationOutcome.ERROR]
    assert len(warning_messages) == 1
    assert len(error_messages) == 1
    assert "Unused parameter" in warning_messages[0].message
    assert "'c'" in warning_messages[0].message
    assert "Undeclared parameter" in error_messages[0].message
    assert "'b'" in error_messages[0].message
