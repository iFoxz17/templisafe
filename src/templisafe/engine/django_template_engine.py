from __future__ import annotations

from typing import Any

from overrides import overrides

from templisafe.engine.template_engine import TemplateEngine
from templisafe.settings.template_engine_settings import TemplateEngineSettings


class DjangoTemplateEngine(TemplateEngine):
    """
    Parses templates using a Django template Engine and extracts variables.
    Lazy-imports Django at runtime. Raises ImportError if Django is not installed.
    """

    __slots__: tuple[str, ...] = (
        "_Engine",
        "_env",
        "_VariableNode",
        "_NodeList",
        "_Node",
    )

    def __init__(self, settings: TemplateEngineSettings) -> None:
        super().__init__(settings)

        try:
            django_template: Any = __import__("django.template", fromlist=["Engine"])
            django_base: Any = __import__("django.template.base", fromlist=["Node", "NodeList", "VariableNode"])
        except ImportError:
            raise ImportError("Django is not installed. Please install Django to use this template engine.")

        Engine = django_template.Engine
        Node = django_base.Node
        NodeList = django_base.NodeList
        VariableNode = django_base.VariableNode

        self._Engine = Engine
        self._env: Any = Engine(**settings.config)
        self._VariableNode = VariableNode
        self._NodeList = NodeList
        self._Node = Node

    @overrides
    def extract_variables(self, template_str: str) -> set[str]:
        django_template: Any = __import__("django.template", fromlist=["Template"])

        template = django_template.Template(template_str, engine=self._env)
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
        django_template: Any = __import__("django.template", fromlist=["Context", "Template"])

        template = django_template.Template(template_str, engine=self._env)
        context = django_template.Context(vars_map)
        return template.render(context)
