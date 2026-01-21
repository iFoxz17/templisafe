import pytest

from templisafe import (
    SourceSettings,
    TemplaterFactory,
    Templater,
    Build
)
from templisafe.template.template_model import Parameterization, Rendering, RenderingSpec

TEMPLATE_YAML_STR: str = (
"""
Hello {{ community }}! 
I am a {{ language_list }} developer.
I am specialized in developing complex objects like {{ complex_object }}.
"""
)

SCHEMA_YAML_STR: str = (
"""
schema:
    community: str
    language_list: list[str]
    complex_object: dict[str, list[float]]
"""
)

VARIANTS_1_YAML_STR = """
variants:
  - name: python
    bindings:
      community: Python community
      language_list: 
        - python
      complex_object:
        top1:
          - 2.3
          - 3.5
          - 4.1
        top2:
          - 1.1
          - 7.8
          
  - name: oop
    bindings:
      community: OOP community
      language_list: [java, c++, c#, ruby, python]
      complex_object:
        top3:
          - 9.7
          - 1.3
        top4:
          - 5.6
          - 8.7
"""

VARIANTS_2_YAML_STR = """
variants:
  - name: functional
    bindings:
      community: Functional community
      language_list: [python, lisp, javascript]
      complex_object:
        top5:
          - 19.2
        top6:
          - 3.4
          - 4.5
"""

def test_full_build_with_local_sources(tmp_path):
    # ------------------------------------------------------------------
    # Create temporary resource files
    # ------------------------------------------------------------------
    template_file = tmp_path / "template.j2"
    template_file.write_text(TEMPLATE_YAML_STR)

    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text(SCHEMA_YAML_STR)

    variants_1_file = tmp_path / "variants1.yaml"
    variants_1_file.write_text(VARIANTS_1_YAML_STR)

    variants_2_file = tmp_path / "variants2.yaml"
    variants_2_file.write_text(VARIANTS_2_YAML_STR)

    # ------------------------------------------------------------------
    # Create SourceSettings (LOCAL)
    # ------------------------------------------------------------------
    template_source = SourceSettings.create(
        kind="local",
        path=str(template_file),
    )

    schema_source = SourceSettings.create(
        kind="local",
        path=str(schema_file),
    )

    variants_1_source = SourceSettings.create(
        kind="local",
        path=str(variants_1_file),
    )

    variants_2_source = SourceSettings.create(
        kind="local",
        path=str(variants_2_file),
    )

    # ------------------------------------------------------------------
    # Create templater
    # ------------------------------------------------------------------
    templater: Templater = TemplaterFactory().create()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    build: Build = templater.build(
        template=template_source,
        schema=schema_source,
        variants=[variants_1_source, variants_2_source],
    )

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------
    rendering: Rendering = build.rendering
    rendered: RenderingSpec = rendering.rendered
    
    assert rendered.names == {"python", "oop", "functional"}

    python_param: Parameterization = rendered["python"]
    assert "Python community" in python_param.rendered_str
    assert "python" in python_param.rendered_str

    oop_param: Parameterization = rendered["oop"]
    assert "OOP community" in oop_param.rendered_str
    assert all([l in oop_param.rendered_str for l in ("java", "c++", "c#", "ruby", "python")])

    functional_param: Parameterization = rendered["functional"]
    assert "Functional community" in functional_param.rendered_str
    assert all([l in functional_param.rendered_str for l in ("python", "lisp", "javascript")])


def test_full_build_with_inline_sources():
    # ------------------------------------------------------------------
    # Create SourceSettings (INLINE)
    # ------------------------------------------------------------------
    template_source = SourceSettings.create(
        kind="inline",
        content_type="text",
        content=TEMPLATE_YAML_STR
    )

    schema_source = SourceSettings.create(
        kind="inline",
        content_type="yaml",
        content=SCHEMA_YAML_STR
    )

    variants_1_source = SourceSettings.create(
        kind="inline",
        content_type="yaml",
        content=VARIANTS_1_YAML_STR
    )

    variants_2_source = SourceSettings.create(
        kind="inline",
        content_type="yaml",
        content=VARIANTS_2_YAML_STR
    )

    # ------------------------------------------------------------------
    # Create templater
    # ------------------------------------------------------------------
    templater: Templater = TemplaterFactory().create()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    build: Build = templater.build(
        template=template_source,
        schema=schema_source,
        variants=[variants_1_source, variants_2_source],
    )

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------
    rendering: Rendering = build.rendering
    rendered: RenderingSpec = rendering.rendered
    
    assert rendered.names == {"python", "oop", "functional"}

    python_param: Parameterization = rendered["python"]
    assert "Python community" in python_param.rendered_str
    assert "python" in python_param.rendered_str

    oop_param: Parameterization = rendered["oop"]
    assert "OOP community" in oop_param.rendered_str
    assert all([l in oop_param.rendered_str for l in ("java", "c++", "c#", "ruby", "python")])

    functional_param: Parameterization = rendered["functional"]
    assert "Functional community" in functional_param.rendered_str
    assert all([l in functional_param.rendered_str for l in ("python", "lisp", "javascript")])
