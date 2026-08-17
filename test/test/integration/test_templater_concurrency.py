from concurrent.futures import ThreadPoolExecutor

from templisafe import Outcome, SchemaInput, TemplateInput, TemplaterFactory, VariableInput, VariantInput
from templisafe.core.util import DiagnosticPolicy


def test_shared_templater_handles_concurrent_build_requests() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)
    schema = SchemaInput(
        schema={
            "worker": "str",
            "index": "int",
            "label": VariableInput(type="str", default="stable"),
        }
    )

    def build_case(index: int) -> str:
        build = templater.build(
            template=TemplateInput(template="{{ worker }}:{{ index }}:{{ label }}"),
            schema=schema,
            variants=VariantInput(name=f"worker_{index}", bindings={"worker": f"w{index}", "index": index}),
        )

        assert build.outcome == Outcome.SUCCESS
        return build.rendering.rendered[f"worker_{index}"].rendered_str

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(build_case, range(40)))

    assert results == [f"w{index}:{index}:stable" for index in range(40)]


def test_shared_templater_handles_concurrent_render_and_validate_requests() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)
    compilation = templater.compile(
        template=TemplateInput(template="{{ user }}={{ score }}"),
        schema=SchemaInput(schema={"user": "str", "score": "int"}),
    )

    def render_case(index: int) -> tuple[Outcome, Outcome, str]:
        variant = VariantInput(name=f"user_{index}", bindings={"user": f"u{index}", "score": index})

        validation = templater.validate(compiled=compilation.compiled, variants=variant)
        rendering = templater.render(compiled=compilation.compiled, variants=variant)

        return (
            validation.outcome,
            rendering.outcome,
            rendering.rendered[f"user_{index}"].rendered_str,
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(render_case, range(40)))

    assert results == [(Outcome.SUCCESS, Outcome.SUCCESS, f"u{index}={index}") for index in range(40)]
