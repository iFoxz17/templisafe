from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.compiler.compiler_resolver import CompilerResolver


class CompilerProvider:
    """Provides `Compiler` instances for a given settings."""

    __slots__: tuple[str, ...] = ("_compiler_resolver",)

    def __init__(self, compiler_resolver: CompilerResolver) -> None:
        self._compiler_resolver: CompilerResolver = compiler_resolver

    def provide(self, compiler: Compiler | CompilerSettings | None = None) -> Compiler:
        """
        Provide a `Compiler` instance for the given settings.

        Parameters
        ----------
        compiler: Compiler | CompilerSettings | None
            Optionally, a specific compiler or settings.

        Returns
        -------
        Compiler
            The compiler instance for the given input.
        """

        return self._compiler_resolver.resolve(compiler)
