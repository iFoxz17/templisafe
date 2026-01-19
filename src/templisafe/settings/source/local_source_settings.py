from overrides import overrides
from templisafe.settings.source.source_settings import SourceSettings, SourceKind

class LocalSourceSettings(SourceSettings):
    path: str

    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.LOCAL


# Register subclass
SourceSettings.register_source_kind(SourceKind.LOCAL, LocalSourceSettings)

