from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.manager_settings import ManagerSettings
from templisafe.template.compiler.compiler import Compiler

# ---------------------------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------------------------


class CompilerFactory:
    """Creates `Compiler` instances from compiler settings."""

    __slots__: tuple[str, ...] = ()

    def create(self, settings: CompilerSettings) -> Compiler:
        """Create a `Compiler` instance for the given settings."""

        return Compiler(settings)


# ---------------------------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------------------------


class CompilerManager:
    """Manages the retrieval of `Compiler` instances."""

    __slots__: tuple[str, ...] = ("_settings", "_factory", "_compilers")

    def __init__(
        self,
        settings: ManagerSettings,
        factory: CompilerFactory | None = None,
        compilers: dict[CompilerSettings, Compiler] | None = None,
    ) -> None:
        self._settings: ManagerSettings = settings
        self._factory: CompilerFactory = factory or CompilerFactory()
        self._compilers: dict[CompilerSettings, Compiler] = compilers or {}

    def get_or_create(self, settings: CompilerSettings) -> Compiler:
        """Return a `Compiler` instance according to the given settings."""

        c: dict[CompilerSettings, Compiler] = self._compilers
        if settings in c:
            return c[settings]

        compiler: Compiler = self._factory.create(settings)
        if self._settings.cache:
            c[settings] = compiler
        return compiler

    def __contains__(self, settings: CompilerSettings) -> bool:
        """Return whether a `Compiler` instance for the given settings is cached."""
        return settings in self._compilers
