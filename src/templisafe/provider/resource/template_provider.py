from templisafe.engine.template_engine import TemplateEngine
from templisafe.parser.template.template_parser import Template, TemplateParser


class TemplateProvider:
    """Provides `Template` instances from raw template strings."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def provide(
        self,
        template_str: str,
        engine: TemplateEngine,
        parser: TemplateParser,
    ) -> Template:
        """
        Parse a template string into a `Template`.

        The method first extracts variable names using the given
        `TemplateEngine`, then delegates parsing to the supplied
        `TemplateParser`.

        Parameters
        ----------
        template_str: str
            The raw template string to parse.
        engine: TemplateEngine
            The engine used to extract variables from the template.
        parser: TemplateParser
            The parser responsible for producing the `Template`.

        Returns
        -------
        Template
            The parsed template instance.
        """

        vars: set[str] = engine.extract_variables(template_str)
        return parser.parse(template_str, vars)
