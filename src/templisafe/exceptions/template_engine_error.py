from templisafe.settings.template_engine_settings import TemplateEngineKind

class TemplateEngineError(Exception):
    """Base class for template engine related exceptions."""
    pass

class UnsupportedTemplateEngineError(TemplateEngineError):
    """Raised when trying to instantiate a TemplateEngine that is not supported."""
    
    __slots__: tuple[str, ...] = ("kind",)

    def __init__(self, kind: TemplateEngineKind) -> None:
        self.kind: TemplateEngineKind = kind
        super().__init__(f"Missing template engine implementation for kind: {kind!r}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(kind={self.kind!r})"