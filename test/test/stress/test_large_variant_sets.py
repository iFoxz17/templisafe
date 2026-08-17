import pytest

from templisafe import (
    ContentType,
    Outcome,
    SchemaInput,
    SourceSettings,
    TemplateInput,
    TemplaterFactory,
)
from templisafe.core.util import DiagnosticPolicy

pytestmark = pytest.mark.integration


def inline_variant_source(index: int) -> SourceSettings:
    return SourceSettings.create(
        kind="inline",
        content=f"""
variants:
  name: variant_{index}
  bindings:
    index: {index}
    name: name_{index}
    active: {str(index % 2 == 0).lower()}
""",
        content_type=ContentType.YAML,
    )


def test_build_renders_ten_thousand_inline_variant_sources() -> None:
    variant_count = 10_000
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ index }}|{{ name }}|{{ active }}"),
        schema=SchemaInput(schema={"index": "int", "name": "str", "active": "bool"}),
        variants=[inline_variant_source(index) for index in range(variant_count)],
    )

    rendered = build.rendering.rendered

    assert build.outcome == Outcome.SUCCESS
    assert len(rendered.names) == variant_count
    assert rendered["variant_0"].rendered_str == "0|name_0|True"
    assert rendered["variant_5000"].rendered_str == "5000|name_5000|True"
    assert rendered["variant_9999"].rendered_str == "9999|name_9999|False"
