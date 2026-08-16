import pytest

from templisafe import Build, Compilation, ContentType, Outcome, Rendering, SourceSettings, TemplaterFactory
from templisafe.core.util import DiagnosticPolicy
from templisafe.exceptions.rendering_error import RenderingFailureError


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

    validation = templater.validate(compiled=compilation.compiled, variants=variants)
    assert validation.outcome == Outcome.SUCCESS
    with pytest.raises(RenderingFailureError):
        _ = validation.rendered

    rendering = templater.render(compiled=compilation.compiled, variants=variants)
    assert isinstance(rendering, Rendering)
    assert rendering.outcome == Outcome.SUCCESS
    assert rendering.rendered["base"].rendered_str == "Hello Ada. Score=42. Label=None."

    build = templater.build(template=template, schema=schema, variants=variants)
    assert isinstance(build, Build)
    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered["base"].rendered_str == rendering.rendered["base"].rendered_str


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


def test_compile_reports_unused_schema_variables_as_warning() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    compilation = templater.compile(
        template=inline_source("Hello {{ name }}", ContentType.TEXT),
        schema=inline_source(
            """
schema:
  name: str
  unused:
    type: int
    default: 1
""",
            ContentType.YAML,
        ),
    )

    assert compilation.outcome == Outcome.WARNING
    assert len(compilation.diagnostics) == 1
    diagnostic = compilation.diagnostics[0]
    assert diagnostic.name == "unused"
    assert diagnostic.index == 1
    assert "Unused variable" in diagnostic.message


def test_render_with_extra_binding_returns_warning_and_output() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)
    compilation = templater.compile(
        template=inline_source("Hello {{ name }}", ContentType.TEXT),
        schema=inline_source(
            """
schema:
  name: str
""",
            ContentType.YAML,
        ),
    )

    rendering = templater.render(
        compiled=compilation.compiled,
        variants=inline_source(
            """
variants:
  name: extra
  bindings:
    name: Ada
    nickname: countess
""",
            ContentType.YAML,
        ),
    )

    assert rendering.outcome == Outcome.WARNING
    assert rendering.rendered["extra"].rendered_str == "Hello Ada"
    assert any(diagnostic.name == "nickname" for diagnostic in rendering.diagnostics)
    assert any("Extra binding" in diagnostic.message for diagnostic in rendering.diagnostics)


def test_build_with_implicit_unnamed_variant_uses_default_name() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=inline_source("Label={{ label }} Score={{ score }}", ContentType.TEXT),
        schema=inline_source(
            """
schema:
  label: str
  score: int
""",
            ContentType.YAML,
        ),
        variants=inline_source(
            """
variants:
  label: alpha
  score: 7
""",
            ContentType.YAML,
        ),
    )

    assert build.outcome == Outcome.SUCCESS
    assert build.rendering.rendered.names == {"default_1"}
    assert build.rendering.rendered["default_1"].rendered_str == "Label=alpha Score=7"


def test_validate_warning_has_no_rendered_output() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)
    compilation = templater.compile(
        template=inline_source("{{ label }}", ContentType.TEXT),
        schema=inline_source(
            """
schema:
  label: str
""",
            ContentType.YAML,
        ),
    )

    validation = templater.validate(
        compiled=compilation.compiled,
        variants=inline_source(
            """
variants:
  name: extra
  bindings:
    label: stable
    unused: ignored
""",
            ContentType.YAML,
        ),
    )

    assert validation.outcome == Outcome.WARNING
    with pytest.raises(RenderingFailureError):
        _ = validation.rendered
