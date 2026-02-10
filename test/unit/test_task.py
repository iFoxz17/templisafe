from pydantic import BaseModel
import pytest
from templisafe.task import (
    TaskBundle, CompilationBundle, RenderingBundle, BuildBundle, Task, TaskType
)
from templisafe.template.template_model import CompilationSpec, Schema, Template
from templisafe.parser.config.config_parser import Config

# -------------------------
# TaskBundle base class
# -------------------------

def test_taskbundle_is_abstract():
    with pytest.raises(TypeError):
        TaskBundle()  # type: ignore

# -------------------------
# CompilationBundle
# -------------------------

def test_compilation_bundle_properties():
    bundle = CompilationBundle(template="my_template")
    assert bundle.template == "my_template"
    assert bundle.type_ == TaskType.COMPILATION

# -------------------------
# RenderingBundle
# -------------------------

def test_rendering_bundle_properties():
    compiled = CompilationSpec(
        template=Template('t', set()),
        schema=(Schema(BaseModel))
    )
    variants = {"key": "value"}
    bundle = RenderingBundle(compiled=compiled, variants=variants)
    assert bundle.compiled == compiled
    assert bundle.variants == variants
    assert bundle.type_ == TaskType.RENDERING

# -------------------------
# BuildBundle
# -------------------------

def test_build_bundle_properties():
    variants = {"key": "v"}
    bundle = BuildBundle(template="t", variants=variants)
    assert bundle.template == "t"
    assert bundle.variants == variants
    assert bundle.type_ == TaskType.BUILD

# -------------------------
# Task container
# -------------------------

def test_task_type_inference():
    compilation_bundle = CompilationBundle(template="t")
    compiled = CompilationSpec(
        template=Template('t', set()),
        schema=(Schema(BaseModel))
    )
    rendering_bundle = RenderingBundle(compiled=compiled, variants={})
    build_bundle = BuildBundle(template="t", variants={})

    task1 = Task(bundle=compilation_bundle)
    task2 = Task(bundle=rendering_bundle)
    task3 = Task(bundle=build_bundle)

    assert task1.type_ == TaskType.COMPILATION
    assert task2.type_ == TaskType.RENDERING
    assert task3.type_ == TaskType.BUILD
