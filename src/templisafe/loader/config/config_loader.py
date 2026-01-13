from typing import Any

from templisafe.exceptions.load_error import UnsopportedLoadError
from templisafe.settings.settings import Settings
from templisafe.loader.loader import Loader, YamlLoader, JsonLoader, TomlLoader
from templisafe.source.source import Source
from templisafe.util.util import ContentType

class ConfigLoader:
    __slots__: tuple[str, ...] = ('_yaml_loader', '_json_loader', '_toml_loader')
    
    def __init__(self) -> None:
        self._yaml_loader: YamlLoader | None = None
        self._json_loader: JsonLoader | None = None
        self._toml_loader: TomlLoader | None = None

    def load_config(self, config_source: Source) -> dict[str, Any]:
        raw: str = config_source.read()
        loader: Loader
        match config_source.content_type:
            case ContentType.YAML:
                if self._yaml_loader is None:
                    self._yaml_loader = YamlLoader()
                loader = self._yaml_loader 
            case ContentType.JSON:
                if self._json_loader is None:
                    self._json_loader = JsonLoader()
                loader = self._json_loader
            case ContentType.TOML:
                if self._toml_loader is None:
                    self._toml_loader = TomlLoader()
                loader = self._toml_loader
            case _:
                raise UnsopportedLoadError(config_source.content_type)
            
        return loader.load(raw)

    def load_settings(self, settings_source: Source) -> Settings:
        config: dict[str, Any] = self.load_config(settings_source)
        return Settings.from_dict(config)