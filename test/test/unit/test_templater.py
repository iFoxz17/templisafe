import pytest

from templisafe import ContentType, SourceSettings, TemplaterFactory
from templisafe.core.util import DiagnosticPolicy
from templisafe.template.template_model import Build, Compilation, Outcome, Rendering

TEMPLATE = "Hello {{ name }}!"
SCHEMA = """
schema:
  name: str
  suffix:
    type: optional[str]
    default: null
"""
VARIANTS = """
variants:
  - name: world
    bindings:
      name: World
"""


@pytest.fixture
def template_source():
    return SourceSettings.create(
        kind="inline",
        content_type=ContentType.TEXT,
        content=TEMPLATE,
    )


@pytest.fixture
def schema_source():
    return SourceSettings.create(
        kind="inline",
        content_type=ContentType.YAML,
        content=SCHEMA,
    )


@pytest.fixture
def variants_source():
    return SourceSettings.create(
        kind="inline",
        content_type=ContentType.YAML,
        content=VARIANTS,
    )


@pytest.fixture
def templater():
    return TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)


def test_compile_returns_compilation(templater, template_source, schema_source):
    result = templater.compile(template=template_source, schema=schema_source)

    assert isinstance(result, Compilation)
    assert result.outcome == Outcome.WARNING
    assert result.compiled.template.vars == {"name"}


def test_render_returns_rendering(templater, template_source, schema_source, variants_source):
    compilation = templater.compile(template=template_source, schema=schema_source)

    result = templater.render(
        compiled=compilation.compiled,
        variants=variants_source,
    )

    assert isinstance(result, Rendering)
    assert result.outcome == Outcome.SUCCESS
    assert result.rendered["world"].rendered_str == "Hello World!"


def test_validate_returns_rendering(templater, template_source, schema_source, variants_source):
    compilation = templater.compile(template=template_source, schema=schema_source)

    result = templater.validate(
        compiled=compilation.compiled,
        variants=variants_source,
    )

    assert isinstance(result, Rendering)
    assert result.outcome == Outcome.SUCCESS


def test_build_returns_build(templater, template_source, schema_source, variants_source):
    result = templater.build(
        template=template_source,
        schema=schema_source,
        variants=variants_source,
    )

    assert isinstance(result, Build)
    assert result.outcome == Outcome.WARNING
    assert result.rendering.rendered["world"].rendered_str == "Hello World!"
