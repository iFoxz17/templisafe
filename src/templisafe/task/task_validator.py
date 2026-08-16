from templisafe.task.task import (
    BuildBundle,
    CompilationBundle,
    RenderingBundle,
    Task,
    TaskType,
)
from templisafe.template.template_model import CompilationSpec


class TaskValidator:
    """Validate public tasks before they enter the service pipeline."""

    __slots__: tuple[str, ...] = ()

    def validate(self, task: Task) -> None:
        bundle = task.bundle

        if task.type is TaskType.COMPILATION:
            if not isinstance(bundle, CompilationBundle):
                raise TypeError("Compilation tasks must contain a CompilationBundle")
            if bundle.template is None:
                raise ValueError("Compilation tasks require a template")
            return

        if task.type is TaskType.RENDERING:
            if not isinstance(bundle, RenderingBundle):
                raise TypeError("Rendering tasks must contain a RenderingBundle")
            if not isinstance(bundle.compiled, CompilationSpec):
                raise TypeError("Rendering tasks require a CompilationSpec")
            if bundle.variants is None:
                raise ValueError("Rendering tasks require variants")
            return

        if task.type is TaskType.BUILD:
            if not isinstance(bundle, BuildBundle):
                raise TypeError("Build tasks must contain a BuildBundle")
            if bundle.template is None:
                raise ValueError("Build tasks require a template")
            if bundle.variants is None:
                raise ValueError("Build tasks require variants")
            return

        raise ValueError(f"Unsupported task type: {task.type}")
