from overrides import overrides
from templisafe.settings.source.source_settings import SourceSettings, SourceKind

class InlineSourceSettings(SourceSettings):
    content: str

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.INLINE

# Register subclass
SourceSettings.register_source_kind(SourceKind.INLINE, InlineSourceSettings)
