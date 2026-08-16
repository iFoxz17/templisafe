import pytest

from templisafe import (
    Outcome,
    SchemaInput,
    TemplateInput,
    TemplaterFactory,
    VariableInput,
    VariantInput,
    VariantSetInput,
)
from templisafe.core.util import DiagnosticPolicy
from templisafe.exceptions.variant_error import IllegalVariantError

VALID_SCORE_SCHEMA = SchemaInput(
    schema={
        "name": "str",
        "score": {
            "type": "int",
            "constraints": {
                "gt": 0,
                "lt": 101,
            },
        },
    }
)


def test_build_accepts_public_input_models() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ name }} scored {{ score }}"),
        schema=VALID_SCORE_SCHEMA,
        variants=VariantSetInput(
            variants=[
                VariantInput(name="ada", bindings={"name": "Ada", "score": 42}),
                VariantInput(name="grace", bindings={"name": "Grace", "score": 99}),
            ]
        ),
    )

    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered["ada"].rendered_str == "Ada scored 42"
    assert build.rendering.rendered["grace"].rendered_str == "Grace scored 99"


def test_validate_and_render_accept_single_variant_input() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)
    compilation = templater.compile(
        template=TemplateInput(template="{{ name }} scored {{ score }}"),
        schema=VALID_SCORE_SCHEMA,
    )

    variant = VariantInput(name="ada", bindings={"name": "Ada", "score": 42})

    validation = templater.validate(compiled=compilation.compiled, variants=variant)
    assert validation.outcome == Outcome.SUCCESS

    rendering = templater.render(compiled=compilation.compiled, variants=variant)
    assert rendering.outcome == Outcome.SUCCESS
    assert rendering.rendered["ada"].rendered_str == "Ada scored 42"


def test_build_accepts_schema_input_model() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ name }} scored {{ score }}"),
        schema=SchemaInput(
            schema={
                "name": "str",
                "score": {
                    "type": "int",
                    "constraints": {
                        "gt": 0,
                        "lt": 101,
                    },
                },
            }
        ),
        variants=VariantInput(name="ada", bindings={"name": "Ada", "score": 42}),
    )

    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered["ada"].rendered_str == "Ada scored 42"


def test_dynamic_variant_input_reports_schema_validation_errors() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)
    compilation = templater.compile(
        template=TemplateInput(template="{{ name }} scored {{ score }}"),
        schema=VALID_SCORE_SCHEMA,
    )

    rendering = templater.render(
        compiled=compilation.compiled,
        variants=VariantInput(name="invalid", bindings={"name": "Ada", "score": 0}),
    )

    assert rendering.outcome == Outcome.ERROR
    assert any(diagnostic.name == "score" for diagnostic in rendering.diagnostics)


def test_build_accepts_variable_input_objects() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ name }} scored {{ score }}"),
        schema=SchemaInput(
            schema={
                "name": VariableInput(type="str"),
                "score": VariableInput(type="int", constraints={"gt": 0, "lt": 101}),
            }
        ),
        variants=VariantInput(name="ada", bindings={"name": "Ada", "score": 42}),
    )

    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered["ada"].rendered_str == "Ada scored 42"


def test_variant_set_input_accepts_implicit_named_mapping() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ user }}={{ score }}"),
        schema=SchemaInput(schema={"user": "str", "score": "int"}),
        variants=VariantSetInput(
            variants={
                "ada": {"user": "Ada", "score": 42},
                "grace": {"user": "Grace", "score": 99},
            }
        ),
    )

    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered.names == {"ada", "grace"}
    assert build.rendering.rendered["ada"].rendered_str == "Ada=42"
    assert build.rendering.rendered["grace"].rendered_str == "Grace=99"


def test_schema_input_default_is_used_for_missing_dynamic_binding() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ user }} [{{ label }}]"),
        schema=SchemaInput(
            schema={
                "user": "str",
                "label": VariableInput(type="str", default="stable"),
            }
        ),
        variants=VariantInput(name="ada", bindings={"user": "Ada"}),
    )

    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered["ada"].rendered_str == "Ada [stable]"


def test_duplicate_dynamic_variant_names_raise() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    with pytest.raises(IllegalVariantError):
        templater.build(
            template=TemplateInput(template="{{ user }}"),
            schema=SchemaInput(schema={"user": "str"}),
            variants=VariantSetInput(
                variants=[
                    VariantInput(name="duplicate", bindings={"user": "Ada"}),
                    VariantInput(name="duplicate", bindings={"user": "Grace"}),
                ]
            ),
        )
