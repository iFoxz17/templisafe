from __future__ import annotations
from typing import Any, TYPE_CHECKING, Callable
from overrides import overrides

from templisafe.engine.template_engine import TemplateEngine

if TYPE_CHECKING:
    from templisafe.settings.template_engine_settings import CustomTemplateEngineSettings

class CustomTemplateEngine(TemplateEngine):
    """
    A template engine that delegates variable extraction and rendering to user-provided callables.

    This engine is intended for use with `CustomTemplateEngineSettings`, allowing fully
    custom behavior for template parsing and rendering. Users provide:

        - `extract_variables_func`: a callable that takes a template string and returns a set of variable names.
        - `render_func`: a callable that takes a template string and a mapping of values, returning the rendered string.

    Example usage with `CustomTemplateEngineSettings`:

        def extract_vars(template: str) -> set[str]:
            return {"x", "y"}

        def render(template: str, values: dict[str, Any]) -> str:
            return template.replace("{{x}}", str(values["x"])).replace("{{y}}", str(values["y"]))

        settings = CustomTemplateEngineSettings(
            kind=TemplateEngineKind.CUSTOM,
            config={},
            extract_variables_func=extract_vars,
            render_func=render
        )

        engine = CustomTemplateEngine(settings)
        engine.extract_variables("Hello {{x}} and {{y}}")  # returns {'x', 'y'}
        engine.render("Hello {{x}} and {{y}}", {"x": 1, "y": 2})  # returns 'Hello 1 and 2'
    """

    __slots__: tuple[str, ...] = ("_extract_vars_func", "_render_func")

    def __init__(self, settings: CustomTemplateEngineSettings) -> None:
        super().__init__(settings)

        self._extract_vars_func: Callable[[str], set[str]] = settings.extract_variables_func
        self._render_func: Callable[[str, dict[str, Any]], str] = settings.render_func

    @overrides
    def extract_variables(self, template_str: str) -> set[str]:
        return self._extract_vars_func(template_str)

    @overrides
    def render(self, template_str: str, vars_map: dict[str, Any]) -> str:        
        return self._render_func(template_str, vars_map)
