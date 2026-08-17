import pytest

from templisafe import (
    Build,
    ContentType,
    Parameterization,
    Rendering,
    RenderingSpec,
    SchemaInput,
    SourceSettings,
    TemplateInput,
    Templater,
    TemplaterFactory,
    VariableInput,
    VariantInput,
    VariantSetInput,
)
from templisafe.core.util import DiagnosticPolicy
from templisafe.exceptions.variant_error import IllegalVariantError

TEMPLATE_YAML_STR: str = """
Hello {{ community }}!
I am a {{ language_list }} developer.
I am specialized in developing complex objects like {{ complex_object }}.
"""

SCHEMA_YAML_STR: str = """
schema:
    community: str
    language_list: list[str]
    complex_object: dict[str, list[float]]
"""

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


def inline_source(content: str, content_type: ContentType | str) -> SourceSettings:
    return SourceSettings.create(
        kind="inline",
        content=content,
        content_type=content_type,
    )


def assert_community_rendering(rendering: Rendering) -> None:
    rendered: RenderingSpec = rendering.rendered

    assert rendered.names == {"python", "oop", "functional"}

    python_param: Parameterization = rendered["python"]
    assert "Python community" in python_param.rendered_str
    assert "python" in python_param.rendered_str

    oop_param: Parameterization = rendered["oop"]
    assert "OOP community" in oop_param.rendered_str
    assert all(language in oop_param.rendered_str for language in ("java", "c++", "c#", "ruby", "python"))

    functional_param: Parameterization = rendered["functional"]
    assert "Functional community" in functional_param.rendered_str
    assert all(language in functional_param.rendered_str for language in ("python", "lisp", "javascript"))


def test_full_build_with_local_sources(tmp_path) -> None:
    template_file = tmp_path / "template.j2"
    template_file.write_text(TEMPLATE_YAML_STR, encoding="utf-8")

    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text(SCHEMA_YAML_STR, encoding="utf-8")

    variants_1_file = tmp_path / "variants1.yaml"
    variants_1_file.write_text(VARIANTS_1_YAML_STR, encoding="utf-8")

    variants_2_file = tmp_path / "variants2.yaml"
    variants_2_file.write_text(VARIANTS_2_YAML_STR, encoding="utf-8")

    templater: Templater = TemplaterFactory().create()
    build: Build = templater.build(
        template=SourceSettings.create(kind="local", path=str(template_file)),
        schema=SourceSettings.create(kind="local", path=str(schema_file)),
        variants=[
            SourceSettings.create(kind="local", path=str(variants_1_file)),
            SourceSettings.create(kind="local", path=str(variants_2_file)),
        ],
    )

    assert_community_rendering(build.rendering)


def test_full_build_with_inline_sources() -> None:
    templater: Templater = TemplaterFactory().create()
    build: Build = templater.build(
        template=inline_source(TEMPLATE_YAML_STR, ContentType.TEXT),
        schema=inline_source(SCHEMA_YAML_STR, ContentType.YAML),
        variants=[
            inline_source(VARIANTS_1_YAML_STR, ContentType.YAML),
            inline_source(VARIANTS_2_YAML_STR, ContentType.YAML),
        ],
    )

    assert_community_rendering(build.rendering)


def test_build_accepts_mixed_source_formats_and_multiple_variant_files(tmp_path) -> None:
    template_file = tmp_path / "message.j2"
    template_file.write_text("{{ name }} scored {{ score }}", encoding="utf-8")

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
            inline_source(
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
            ),
            SourceSettings.create(kind="local", path=str(toml_variants_file)),
        ],
    )

    assert build.outcome == 0
    assert build.rendering.rendered.names == {"json", "toml"}
    assert build.rendering.rendered["json"].rendered_str == "Grace scored 99"
    assert build.rendering.rendered["toml"].rendered_str == "Linus scored 87"


def test_build_accepts_settings_from_sources_with_canonical_schema_and_variant_keys() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=inline_source("{{ name }}={{ score }}:{{ label }}", ContentType.TEXT),
        schema=inline_source(
            """
schema:
  name: str
  score:
    type: int
  label:
    type: optional[str]
    default: stable
""",
            ContentType.YAML,
        ),
        variants=inline_source(
            """
variants:
  - name: sourced_settings
    bindings:
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
default_variants_name: case
""",
            ContentType.YAML,
        ),
        compiler_settings=inline_source("index_key: position", ContentType.YAML),
        renderer_settings=inline_source("index_key: position", ContentType.YAML),
    )

    assert build.outcome == 0
    assert build.rendering.rendered.names == {"sourced_settings"}
    assert build.rendering.rendered["sourced_settings"].rendered_str == "Ada=42:stable"


def test_build_accepts_mixed_dynamic_and_source_variants() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ name }} scored {{ score }}"),
        schema=inline_source(
            """
schema:
  name: str
  score: int
""",
            ContentType.YAML,
        ),
        variants=[
            VariantInput(name="dynamic", bindings={"name": "Ada", "score": 42}),
            inline_source(
                """
variants:
  name: source
  bindings:
    name: Grace
    score: 99
""",
                ContentType.YAML,
            ),
        ],
    )

    assert build.outcome == 0
    assert build.rendering.rendered.names == {"dynamic", "source"}
    assert build.rendering.rendered["dynamic"].rendered_str == "Ada scored 42"
    assert build.rendering.rendered["source"].rendered_str == "Grace scored 99"


def test_build_accepts_template_input_with_local_schema_and_inline_variants(tmp_path) -> None:
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text(
        """
schema:
  name: str
  score: int
""",
        encoding="utf-8",
    )
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ name }} scored {{ score }}"),
        schema=SourceSettings.create(kind="local", path=str(schema_file)),
        variants=inline_source(
            """
variants:
  name: inline
  bindings:
    name: Ada
    score: 42
""",
            ContentType.YAML,
        ),
    )

    assert build.outcome == 0
    assert build.rendering.rendered["inline"].rendered_str == "Ada scored 42"


def test_build_accepts_json_schema_source_and_dynamic_variant() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=TemplateInput(template="{{ user }}={{ score }}"),
        schema=inline_source(
            """
{
  "schema": {
    "user": "str",
    "score": {
      "type": "int",
      "constraints": {
        "gt": 0
      }
    }
  }
}
""",
            ContentType.JSON,
        ),
        variants=VariantInput(name="dynamic", bindings={"user": "Ada", "score": 42}),
    )

    assert build.outcome == 0
    assert build.rendering.rendered["dynamic"].rendered_str == "Ada=42"


def test_build_accepts_schema_input_with_source_and_dynamic_variants() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    build = templater.build(
        template=inline_source("{{ user }}:{{ label }}", ContentType.TEXT),
        schema=SchemaInput(
            schema={
                "user": "str",
                "label": VariableInput(type="str", default="stable"),
            }
        ),
        variants=[
            VariantSetInput(variants={"dynamic": {"user": "Ada"}}),
            inline_source(
                """
variants:
  name: source
  bindings:
    user: Grace
""",
                ContentType.YAML,
            ),
        ],
    )

    assert build.outcome == 0
    assert build.rendering.rendered.names == {"dynamic", "source"}
    assert build.rendering.rendered["dynamic"].rendered_str == "Ada:stable"
    assert build.rendering.rendered["source"].rendered_str == "Grace:stable"


def test_duplicate_variant_names_across_dynamic_and_source_inputs_raise() -> None:
    templater = TemplaterFactory().create(diagnostic_policy=DiagnosticPolicy.IGNORE)

    with pytest.raises(IllegalVariantError):
        templater.build(
            template=TemplateInput(template="{{ user }}"),
            schema=SchemaInput(schema={"user": "str"}),
            variants=[
                VariantInput(name="duplicate", bindings={"user": "Ada"}),
                inline_source(
                    """
variants:
  name: duplicate
  bindings:
    user: Grace
""",
                    ContentType.YAML,
                ),
            ],
        )
