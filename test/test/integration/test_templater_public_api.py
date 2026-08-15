import pytest

from templisafe import ContentType, SourceSettings, TemplaterFactory
from templisafe.core.util import DiagnosticPolicy
from templisafe.exceptions.rendering_error import RenderingFailureError
from templisafe.template.template_model import Build, Compilation, Outcome, Rendering


def inline_source(content: str, content_type: ContentType | str) -> SourceSettings:
    return SourceSettings.create(
        kind="inline",
        content=content,
        content_type=content_type,
    )


def test_compile_render_validate_and_build_with_inline_sources() -> None:
    template = inline_source(
        "Hello {{ name }}. Score={{ score }}. Label={{ label }}.",
        ContentType.TEXT,
    )
    schema = inline_source(
        """
schema:
  name: str
  score: int
  label:
    type: optional[str]
    default: null
""",
        ContentType.YAML,
    )
    variants = inline_source(
        """
variants:
  name: base
  bindings:
    name: Ada
    score: 42
""",
        ContentType.YAML,
    )
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    compilation = templater.compile(template=template, schema=schema)
    assert isinstance(compilation, Compilation)
    assert compilation.outcome == Outcome.SUCCESS
    assert compilation.compiled.template.vars == {"name", "score", "label"}

    rendering = templater.render(compiled=compilation.compiled, variants=variants)
    assert isinstance(rendering, Rendering)
    assert rendering.outcome == Outcome.SUCCESS
    assert rendering.rendered["base"].rendered_str == "Hello Ada. Score=42. Label=None."

    validation = templater.validate(compiled=compilation.compiled, variants=variants)
    assert validation.outcome == Outcome.SUCCESS
    with pytest.raises(RenderingFailureError):
        _ = validation.rendered

    build = templater.build(template=template, schema=schema, variants=variants)
    assert isinstance(build, Build)
    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered["base"].rendered_str == rendering.rendered["base"].rendered_str


def test_build_accepts_mixed_source_formats_and_multiple_variant_files(
    tmp_path,
) -> None:
    template_file = tmp_path / "message.j2"
    template_file.write_text("{{ name }} scored {{ score }}", encoding="utf-8")

    json_variants = inline_source(
        """
{
  "variants": [
    {
      "name": "json",
      "bindings": {
        "name": "Grace",
        "score": 99
      }
    }
  ]
}
""",
        ContentType.JSON,
    )

    toml_variants_file = tmp_path / "variants.toml"
    toml_variants_file.write_text(
        """
[[variants]]
name = "toml"

[variants.bindings]
name = "Linus"
score = 87
""",
        encoding="utf-8",
    )

    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)
    build = templater.build(
        template=SourceSettings.create(kind="local", path=str(template_file)),
        schema=inline_source(
            """
schema:
  name: str
  score: int
""",
            ContentType.YAML,
        ),
        variants=[
            json_variants,
            SourceSettings.create(kind="local", path=str(toml_variants_file)),
        ],
    )

    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered.names == {"json", "toml"}
    assert build.rendering.rendered["json"].rendered_str == "Grace scored 99"
    assert build.rendering.rendered["toml"].rendered_str == "Linus scored 87"


def test_build_accepts_parser_engine_executor_and_renderer_settings_from_sources() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=inline_source("{{ name }}={{ score }}:{{ label }}", ContentType.TEXT),
        schema=inline_source(
            """
variables:
  name: str
  score:
    kind: int
  label:
    kind: optional[str]
    fallback: stable
""",
            ContentType.YAML,
        ),
        variants=inline_source(
            """
cases:
  - id: custom_keys
    values:
      name: Ada
      score: 42
""",
            ContentType.YAML,
        ),
        template_engine=inline_source("engine_kind: jinja", ContentType.YAML),
        source_executor_settings=inline_source(
            """
strategy: sequential
n_threads: 1
""",
            ContentType.YAML,
        ),
        schema_parser_settings=inline_source(
            """
schema_key: variables
type_key: kind
default_key: fallback
index_key: position
allowed_types:
  - int
  - str
  - optional
""",
            ContentType.YAML,
        ),
        variant_parser_settings=inline_source(
            """
variants_key: cases
variant_name_key: id
bindings_key: values
""",
            ContentType.YAML,
        ),
        compiler_settings=inline_source("index_key: position", ContentType.YAML),
        renderer_settings=inline_source("index_key: position", ContentType.YAML),
    )

    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered.names == {"custom_keys"}
    assert build.rendering.rendered["custom_keys"].rendered_str == "Ada=42:stable"


def test_compile_without_schema_uses_permissive_template_schema() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)
    compilation = templater.compile(
        template=inline_source("Hello {{ name }} from {{ place }}", ContentType.TEXT),
    )

    assert compilation.outcome == Outcome.SUCCESS
    assert set(compilation.compiled.schema.model_cls.model_fields) == {"name", "place"}

    rendering = templater.render(
        compiled=compilation.compiled,
        variants=inline_source(
            """
variants:
  name: no_schema
  bindings:
    name: Ada
    place: London
""",
            ContentType.YAML,
        ),
    )

    assert rendering.outcome == Outcome.SUCCESS
    assert rendering.rendered["no_schema"].rendered_str == "Hello Ada from London"


def test_validate_and_render_report_invalid_variants_without_rendered_output() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)
    compilation = templater.compile(
        template=inline_source("{{ name }}: {{ score }}", ContentType.TEXT),
        schema=inline_source(
            """
schema:
  name: str
  score: int
""",
            ContentType.YAML,
        ),
    )
    variants = inline_source(
        """
variants:
  name: missing_score
  bindings:
    name: Ada
""",
        ContentType.YAML,
    )

    validation = templater.validate(compiled=compilation.compiled, variants=variants)
    assert validation.outcome == Outcome.ERROR
    assert all(diagnostic.name == "score" for diagnostic in validation.diagnostics)
    assert any("Missing required binding" in diagnostic.message for diagnostic in validation.diagnostics)
    with pytest.raises(RenderingFailureError):
        _ = validation.rendered

    rendering = templater.render(compiled=compilation.compiled, variants=variants)
    assert rendering.outcome == Outcome.ERROR
    with pytest.raises(RenderingFailureError):
        _ = rendering.rendered
