import pytest
from typing import Any
from pydantic import create_model, Field
from templisafe.template.template_model import (
    Template,
    Schema,
    Compilation,
    Outcome,
    Template,
    Diagnostic
)
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.template.compiler import Compiler

# ========================
# Fixtures
# ========================

@pytest.fixture
def compiler_settings() -> CompilerSettings:
    return CompilerSettings(index_key="_index")


# ========================
# Tests
# ========================

def test_compile_no_schema_creates_empty_schema(compiler_settings: CompilerSettings):
    compiler = Compiler(compiler_settings)
    template = Template(template_str="SELECT {{ a }}, {{ b }} FROM Table", vars=set(["a", "b"]))
    compilation: Compilation = compiler.compile(template)

    assert compilation.outcome == Outcome.SUCCESS
    assert compilation._spec is not None
    schema_model = compilation._spec.schema.model_cls
    # The empty schema model should have fields for all template vars
    assert set(schema_model.model_fields.keys()) == {"a", "b"}
    assert schema_model.model_fields['a'].annotation is object
    assert schema_model.model_fields['b'].annotation is object
    assert compilation.diagnostics == ()


def test_compile_with_matching_schema_success(compiler_settings: CompilerSettings):
    # Create a schema with the same variables as template
    fields: dict[str, Any] = {"a": (int, ...), "b": (str, ...)}
    model_cls = create_model("TestSchema", **fields)
    schema = Schema(model_cls=model_cls)
    template = Template(template_str="SELECT {{ a }}, {{ b }} FROM Table", vars=set(["a", "b"]))
    
    compiler = Compiler(compiler_settings)
    compilation = compiler.compile(template, schema)

    assert compilation.outcome == Outcome.SUCCESS
    assert compilation._spec is not None
    assert compilation._spec.schema == schema
    assert compilation.diagnostics == ()


def test_compile_with_defaults_and_constraints(compiler_settings: CompilerSettings):
    from pydantic import create_model, Field
    from templisafe.template.template_model import Template, Schema, Outcome
    from templisafe.template.compiler import Compiler

    # Create a schema with defaults and constraints
    fields: dict[str, Any] = {
        "age": (int, Field(default=18, gt=0, lt=150)),
        "name": (str, Field(default="Anonymous", max_length=10)),
        "score": (float, Field(default=0.0, ge=0.0, le=100.0)),
    }
    model_cls = create_model("TestSchema", **fields)
    schema = Schema(model_cls=model_cls)

    template = Template(
        template_str="SELECT {{ age }}, {{ name }}, {{ score }} FROM Users",
        vars=set(["age", "name", "score"])
    )

    compiler = Compiler(compiler_settings)
    compilation = compiler.compile(template, schema)

    # Compilation should succeed with no diagnostics
    assert compilation.outcome == Outcome.SUCCESS
    assert compilation.diagnostics == ()

    # Access compiled Pydantic model
    compiled_model = compilation.compiled.schema.model_cls

    # Check default values
    instance = compiled_model()
    assert getattr(instance, "age") == 18
    assert getattr(instance, "name") == "Anonymous"
    assert getattr(instance, "score") == 0.0

    # Check field annotations and constraints
    age_field = compiled_model.model_fields["age"]
    assert age_field.annotation is int
    assert age_field.metadata
    assert age_field.default is not None
    assert age_field.default == 18
    
    name_field = compiled_model.model_fields["name"]
    assert name_field.annotation is str
    assert name_field.metadata
    assert name_field.default is not None
    assert name_field.default == "Anonymous"
    
    score_field = compiled_model.model_fields["score"]
    assert score_field.annotation is float
    assert score_field.metadata
    assert score_field.default is not None
    assert score_field.default == 0.0

def test_compile_with_unused_variables_generates_warnings(compiler_settings: CompilerSettings):
    fields: dict[str, Any] = {
        "x": (int, Field(..., json_schema_extra={"_index": 0})),
        "y": (str, Field(..., json_schema_extra={"_index": 1})),
        "z": (float, Field(..., json_schema_extra={"_index": 2})),
    }
    model_cls = create_model("TestSchema", **fields)
    schema = Schema(model_cls=model_cls)
    template = Template(template_str="SELECT {{ x }}, {{ y }} FROM Table", vars=set(["x", "y"]))

    compiler = Compiler(compiler_settings)
    compilation = compiler.compile(template, schema)

    assert compilation.outcome == Outcome.WARNING
    assert len(compilation.diagnostics) == 1
    diag = compilation.diagnostics[0]
    assert diag.level == Outcome.WARNING
    assert diag.name == "z"
    assert diag.index == 2
    assert "Unused variable" in diag.message


def test_compile_with_undeclared_variables_generates_error(compiler_settings: CompilerSettings):
    fields: dict[str, Any] = {"x": (int, Field(..., json_schema_extra={"_index": 0}))}
    model_cls = create_model("TestSchema", **fields)
    schema = Schema(model_cls=model_cls)
    template = Template(template_str="SELECT {{ x }}, {{ y }} FROM Table", vars=set(["x", "y"]))

    compiler = Compiler(compiler_settings)
    compilation = compiler.compile(template, schema)

    assert compilation.outcome == Outcome.ERROR
    assert compilation._spec is None
    assert len(compilation.diagnostics) == 1
    diag = compilation.diagnostics[0]
    assert diag.level == Outcome.ERROR
    assert diag.name == "y"
    assert "Undeclared variable" in diag.message


def test_compile_with_unused_and_undeclared_mixed(compiler_settings: CompilerSettings):
    fields: dict[str, Any] = {
        "x": (int, Field(..., json_schema_extra={"_index": 0})),
        "z": (str, Field(..., json_schema_extra={"_index": 1})),
    }
    model_cls = create_model("TestSchema", **fields)
    schema = Schema(model_cls=model_cls)
    template = Template(template_str="SELECT {{ x }}, {{ y }} FROM Table", vars=set(["x", "y"]))

    compiler = Compiler(compiler_settings)
    compilation = compiler.compile(template, schema)

    # If there are any undeclared vars, outcome is ERROR
    assert compilation.outcome == Outcome.ERROR
    # Two diagnostics: one warning (unused), one error (undeclared)
    levels = [d.level for d in compilation.diagnostics]
    assert Outcome.WARNING in levels
    assert Outcome.ERROR in levels
