from templisafe.template.compiler.compiler import Compilation, Compiler
from templisafe.template.template_model import Schema, Template


class CompilationProvider:
    """Provides `Compilation` instances by delegating compilation to a `Compiler`."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def provide(
        self,
        template: Template,
        schema: Schema,
        compiler: Compiler,
    ) -> Compilation:
        """
        Compile a `Template` against a `Schema` using the given `Compiler`.

        Parameters
        ----------
        template: Template
            The template to compile.
        schema: Schema
            The schema to use for compilation validation.
        compiler: Compiler
            The compiler responsible for producing the `Compilation`.

        Returns
        -------
        Compilation
            The compiled result of the template and schema.
        """
        return compiler.compile(template, schema)
