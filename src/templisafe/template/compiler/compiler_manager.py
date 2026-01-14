from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.template.compiler.compiler import Compiler

#---------------------------------------------------------------------------------------------
# Factory
#---------------------------------------------------------------------------------------------

class CompilerFactory:
    def create(self, settings: CompilerSettings) -> Compiler:
        return Compiler(settings)

#---------------------------------------------------------------------------------------------
# Manager
#---------------------------------------------------------------------------------------------

class CompilerManager:
    __slots__: tuple[str, ...] = ("_factory", "_compilers")

    def __init__(self, compilers: dict[CompilerSettings, Compiler] | None = None) -> None:
        self._factory: CompilerFactory = CompilerFactory()
        self._compilers: dict[CompilerSettings, Compiler] = compilers or {}
    
    def get_or_create(self, settings: CompilerSettings) -> Compiler:
        c: dict[CompilerSettings, Compiler] = self._compilers
        if settings not in c:
            c[settings] = self._factory.create(settings)
        return c[settings]

    def __contains__(self, settings: CompilerSettings) -> bool:
        return settings in self._compilers