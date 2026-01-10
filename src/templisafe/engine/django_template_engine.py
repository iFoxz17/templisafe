from __future__ import annotations
from typing import Any, TYPE_CHECKING
from overrides import overrides

from templisafe.settings.template_engine_settings import TemplateEngineSettings
from templisafe.engine.template_engine import TemplateEngine

if TYPE_CHECKING:
    from django.template import Engine

class DjangoTemplateEngine(TemplateEngine):
    """
    Parses templates using a Django template Engine and extracts variables.
    Lazy-imports Django at runtime. Raises ImportError if Django is not installed.
    """

    __slots__: tuple[str, ...] = ("_Engine", "_env", "_VariableNode", "_NodeList", "_Node")

    def __init__(self, settings: TemplateEngineSettings) -> None:
        super().__init__(settings)

        try:
            from django.template import Engine
            from django.template.base import VariableNode, NodeList, Node
        except ImportError:
            raise ImportError(
                "Django is not installed. Please install Django to use this template engine."
            )

        self._Engine = Engine
        self._env: Engine = Engine(**settings.config)
        self._VariableNode = VariableNode
        self._NodeList = NodeList
        self._Node = Node

    @overrides
    def extract_variables(self, template_str: str) -> set[str]:
        from django.template import Template

        template = Template(template_str, engine=self._env)
        variables: set[str] = set()

        def _walk_nodes(nodelist):
            for node in nodelist:
                # VariableNode contains the variable
                if isinstance(node, self._VariableNode):
                    variables.add(str(node.filter_expression))
                # Some nodes have child nodelists
                for attr in ("nodelist", "nodelist_true", "nodelist_false"):
                    child = getattr(node, attr, None)
                    if isinstance(child, self._NodeList):
                        _walk_nodes(child)

        _walk_nodes(template.nodelist)
        return variables

    @overrides
    def render(self, template_str: str, vars_map: dict[str, Any]) -> str:
        from django.template import Template, Context

        template = Template(template_str, engine=self._env)
        context = Context(vars_map)
        return template.render(context)
