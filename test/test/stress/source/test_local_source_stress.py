from pathlib import Path

import pytest

from templisafe import ContentType, Outcome, SchemaInput, SourceSettings, TemplateInput, TemplaterFactory
from templisafe.core.util import DiagnosticPolicy

pytestmark = pytest.mark.integration


def local_variant_source(tmp_path: Path, index: int) -> SourceSettings:
    path = tmp_path / f"variant_{index}.yaml"
    path.write_text(
        f"""
variants:
  name: variant_{index}
  bindings:
    index: {index}
    label: label_{index}
""",
        encoding="utf-8",
    )
    return SourceSettings.create(
        kind="local",
        path=str(path),
        content_type=ContentType.YAML,
    )


def test_build_renders_hundreds_of_local_variant_sources(tmp_path: Path) -> None:
    variant_count = 750
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ index }}:{{ label }}"),
        schema=SchemaInput(schema={"index": "int", "label": "str"}),
        variants=[local_variant_source(tmp_path, index) for index in range(variant_count)],
    )

    rendered = build.rendering.rendered

    assert build.outcome == Outcome.SUCCESS
    assert len(rendered.names) == variant_count
    assert rendered["variant_0"].rendered_str == "0:label_0"
    assert rendered["variant_375"].rendered_str == "375:label_375"
    assert rendered["variant_749"].rendered_str == "749:label_749"
