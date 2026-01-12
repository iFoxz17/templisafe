from templisafe.exceptions.settings_error import SettingsError
from templisafe.settings.settings import Settings
from templisafe.source.source import Source
from templisafe.util.util import ContentType

class SettingsLoader:
    def __init__(self) -> None:
        pass

    def load(self, settings_source: Source) -> Settings:
        content: str = settings_source.read()
        match settings_source.content_type:
            case ContentType.YAML:
                return Settings.from_yaml(content)
            case ContentType.JSON:
                return Settings.from_json(content)
            
        raise SettingsError(f"Invalid settings source content type: {settings_source.content_type}")