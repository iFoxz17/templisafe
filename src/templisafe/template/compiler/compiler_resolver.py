from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.template.compiler.compiler import Compiler
from templisafe.template.compiler.compiler_manager import CompilerManager


class CompilerResolver:
    """Resolves `Compiler` instances."""

    __slots__: tuple[str, ...] = ("_default_settings", "_compiler_manager")

    def __init__(
        self,
        default_settings: CompilerSettings,
        compiler_manager: CompilerManager,
    ) -> None:
        self._default_settings: CompilerSettings = default_settings
        self._compiler_manager: CompilerManager = compiler_manager

    def resolve(self, compiler: Compiler | CompilerSettings | None = None) -> Compiler:
        """
        Resolve a `Compiler` instance.

        This method supports three scenarios based on the type of the `compiler` argument:
        1. If it is already a `Compiler`, it is returned as-is.
        2. If it is a `CompilerSettings`, a `Compiler` based on the given settings is returned.
        3. If it is None, a `Compiler` with default settings is returned.

        Parameters
        ----------
        compiler : Compiler | CompilerSettings | None
            Either an existing compiler, its settings or None to use the default compiler.

        Returns
        -------
        Compiler
            The resolved compiler instance.
        """

        if isinstance(compiler, Compiler):
            return compiler

        settings: CompilerSettings = compiler or self._default_settings
        return self._compiler_manager.get_or_create(settings)
