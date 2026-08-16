import pytest
from pydantic import BaseModel

from templisafe.core.metadata import Metadata, MetaValue
from templisafe.task.task import (
    BuildBundle,
    CompilationBundle,
    FieldCategory,
    RenderingBundle,
    Task,
    TaskType,
)
from templisafe.template.template_model import CompilationSpec, Schema, Template

# ============================================================
# CompilationBundle
# ============================================================


def test_compilation_bundle_properties():
    bundle = CompilationBundle(template="my_template")

    # Field values
    assert bundle.template == "my_template"
    assert bundle.type == TaskType.COMPILATION

    # Metadata classification
    resources = bundle.resources
    components = bundle.components
    assert "template" in resources
    assert "template_parser_settings" in components
    assert components["template_parser_settings"] is None


# ============================================================
# RenderingBundle
# ============================================================


def test_rendering_bundle_properties():
    compiled = CompilationSpec(template=Template("{{ t }}", set()), schema=Schema(BaseModel))
    variants = {"v1": "data"}

    bundle = RenderingBundle(compiled=compiled, variants=variants)

    assert bundle.compiled == compiled
    assert bundle.variants == variants
    assert bundle.type == TaskType.RENDERING

    resources = bundle.resources
    components = bundle.components
    assert "compiled" in resources
    assert "variants" in resources
    assert "renderer_settings" in components
    assert components["renderer_settings"] is None


# ============================================================
# BuildBundle
# ============================================================


def test_build_bundle_properties():
    variants = {"v1": "data"}
    bundle = BuildBundle(template="t", variants=variants)

    assert bundle.template == "t"
    assert bundle.variants == variants
    assert bundle.type == TaskType.BUILD

    resources = bundle.resources
    components = bundle.components
    assert "template" in resources
    assert "variants" in resources
    assert "compiler_settings" in components


# ============================================================
# Task wrapper
# ============================================================


def test_task_type_inference():
    compilation_bundle = CompilationBundle(template="t")
    compiled = CompilationSpec(template=Template("t", set()), schema=Schema(BaseModel))
    rendering_bundle = RenderingBundle(compiled=compiled, variants={"v1": "data"})
    build_bundle = BuildBundle(template="t", variants={"v1": "data"})

    task1 = Task(bundle=compilation_bundle)
    task2 = Task(bundle=rendering_bundle)
    task3 = Task(bundle=build_bundle)

    assert task1.type == TaskType.COMPILATION
    assert task2.type == TaskType.RENDERING
    assert task3.type == TaskType.BUILD


# ============================================================
# Metadata container
# ============================================================


def test_metadata_assignment_and_access():
    meta = Metadata({"key1": MetaValue("val", "desc")}, read_only=False)
    # Access
    assert meta["key1"].value == "val"
    # Assignment allowed
    meta["key2"] = MetaValue(42)
    assert meta["key2"].value == 42
    # Read-only enforcement
    meta_readonly = Metadata({"k": MetaValue(1)})
    with pytest.raises(TypeError):
        meta_readonly["new"] = MetaValue(2)


# ============================================================
# CategoryMetadata helper
# ============================================================


def test_category_metadata_helper():
    from templisafe.task.task import CategoryMetadata

    cat_meta = CategoryMetadata(FieldCategory.COMPONENT)
    val = cat_meta.get("category")
    assert val.value == FieldCategory.COMPONENT
    assert val.description == "Bundle field category"
