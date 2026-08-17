from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from templisafe.task.task import BuildBundle, CompilationBundle, RenderingBundle, Task
from templisafe.task.task_validator import TaskValidator
from templisafe.template.template_model import CompilationSpec, Schema, Template


def test_task_validator_accepts_supported_tasks() -> None:
    validator = TaskValidator()
    compilation_spec = CompilationSpec(template=Template("hello", set()), schema=Schema(BaseModel))

    validator.validate(Task(bundle=CompilationBundle(template="hello")))
    validator.validate(Task(bundle=RenderingBundle(compiled=compilation_spec, variants={"variants": {}})))
    validator.validate(Task(bundle=BuildBundle(template="hello", variants={"variants": {}})))


def test_task_validator_rejects_rendering_without_compilation_spec() -> None:
    validator = TaskValidator()
    bundle = RenderingBundle.model_construct(compiled=Mock(), variants={"variants": {}})
    task = Task.model_construct(bundle=bundle)

    with pytest.raises(TypeError, match="CompilationSpec"):
        validator.validate(task)
