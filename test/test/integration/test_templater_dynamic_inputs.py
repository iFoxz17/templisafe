from pydantic import BaseModel, Field

from templisafe import (
    Outcome,
    SchemaInput,
    TemplateInput,
    TemplaterFactory,
    VariantInput,
    VariantSetInput,
)
from templisafe.core.util import DiagnosticPolicy


class DirectSchema(BaseModel):
    name: str
    score: int = Field(gt=0, lt=101)


def test_build_accepts_public_input_models_and_pydantic_schema() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ name }} scored {{ score }}"),
        schema=DirectSchema,
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
        schema=DirectSchema,
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
        schema=DirectSchema,
    )

    rendering = templater.render(
        compiled=compilation.compiled,
        variants=VariantInput(name="invalid", bindings={"name": "Ada", "score": 0}),
    )

    assert rendering.outcome == Outcome.ERROR
    assert any(diagnostic.name == "score" for diagnostic in rendering.diagnostics)
