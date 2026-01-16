from __future__ import annotations
from typing import Any
from overrides import overrides

from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.engine.template_engine import TemplateEngine

class JinjaTemplateEngine(TemplateEngine):
    """
    Parses templates using a Jinja2 environment and extracts variables.
    Lazy-imports Jinja2 at runtime. Raises ImportError if Jinja2 is not installed.
    """

    __slots__: tuple[str, ...] = ("_env", "_meta")

    def __init__(self, settings: TemplateEngineSettings) -> None:
        super().__init__(settings)

        try:
            from jinja2 import Environment
            from jinja2 import meta
        except ImportError:
            raise ImportError("Jinja2 is not installed. Please install Jinja2 to use this template engine.")

        self._meta = meta
        self._env: Environment = Environment(**settings.config)

    @overrides
    def extract_variables(self, template_str: str) -> set[str]:
        parsed = self._env.parse(template_str)
        return self._meta.find_undeclared_variables(parsed)

    @overrides
    def render(self, template_str: str, vars_map: dict[str, Any]) -> str:
        template = self._env.from_string(template_str)
        return template.render(**vars_map)
