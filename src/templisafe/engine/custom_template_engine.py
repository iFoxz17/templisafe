from __future__ import annotations
from typing import TYPE_CHECKING
from overrides import overrides

from templisafe.engine.template_engine import TemplateEngine

if TYPE_CHECKING:
    from typing import Any, Callable
    from templisafe.settings.template_engine_settings import CustomTemplateEngineSettings
    

class CustomTemplateEngine(TemplateEngine):
    """
    A template engine that delegates variable extraction and rendering
    to user-provided callables.

    This engine is used together with `CustomTemplateEngineSettings` and enables
    fully custom template behavior without requiring users to implement a
    `TemplateEngine` subclass.

    The engine delegates its behavior to two callables provided via settings:

    - `extract_variables_func(template: str, config: dict[str, Any]) -> set[str]`
        Extracts variable names from a template string.

    - `render_func(
            template: str,
            variables: dict[str, Any],
            config: dict[str, Any]
        ) -> str`
        Renders the template using the provided variables.

    The `config` dictionary from `TemplateEngineSettings` is automatically
    passed to both callables.

    Example:

        def extract_vars(template: str, config: dict[str, Any]) -> set[str]:
            return {"x", "y"}

        def render(template: str, values: dict[str, Any], config: dict[str, Any]) -> str:
            return template.replace("{{x}}", str(values["x"])) \
                           .replace("{{y}}", str(values["y"]))

        settings = CustomTemplateEngineSettings(
            kind=TemplateEngineKind.CUSTOM,
            config={"strict": True},                # custom engine property
            extract_variables_func=extract_vars,
            render_func=render,
        )

        engine = CustomTemplateEngine(settings)

        engine.extract_variables("Hello {{x}} and {{y}}")
        # {"x", "y"}

        engine.render("Hello {{x}} and {{y}}", {"x": 1, "y": 2})
        # "Hello 1 and 2"
    """

    __slots__: tuple[str, ...] = ("_extract_vars_func", "_render_func")

    def __init__(self, settings: CustomTemplateEngineSettings) -> None:
        super().__init__(settings)

        self._extract_vars_func: Callable[[str, dict[str, Any]], set[str]] = settings.extract_variables_func
        self._render_func: Callable[[str, dict[str, Any], dict[str, Any]], str] = settings.render_func

    @overrides
    def extract_variables(self, template_str: str) -> set[str]:
        return self._extract_vars_func(template_str, self._settings.config)

    @overrides
    def render(self, template_str: str, vars_map: dict[str, Any]) -> str:        
        return self._render_func(template_str, vars_map, self._settings.config)
