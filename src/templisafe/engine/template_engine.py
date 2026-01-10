from abc import ABC, abstractmethod
from typing import Any

from templisafe.settings.template_engine_settings import TemplateEngineSettings

class TemplateEngine(ABC):
    """Abstract base class representing a template engine."""

    __slots__: tuple[str, ...] = ("_settings",)

    def __init__(self, settings: TemplateEngineSettings) -> None:
        self._settings = settings
                
    @abstractmethod
    def extract_variables(self, template_str: str) -> set[str]:
        """Extract the variables from a template string."""
        pass

    @abstractmethod
    def render(self, template_str: str, vars_map: dict[str, Any]) -> str:
        """Render a template string using the provided variable mappings."""
        pass
