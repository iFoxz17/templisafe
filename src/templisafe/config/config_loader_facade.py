from templisafe.exceptions.config_error import SettingsConfigError
from templisafe.settings.settings import Settings
from templisafe.config.config_loader_manager import ConfigLoaderManager
from templisafe.config.config_loader import Config, ConfigLoader
from templisafe.source.source import Source

class ConfigLoaderFacade:
    """Facade for loading configuration and settings from a source."""

    __slots__: tuple[str, ...] = ('_config_loader_manager',)
    
    def __init__(self, config_loader_manager: ConfigLoaderManager) -> None:
        self._config_loader_manager: ConfigLoaderManager = config_loader_manager
        
    def load_config(self, config_source: Source) -> Config:
        """
        Load a raw configuration from the given source.

        Parameters
        ----------
        config_source : Source
            The source containing configuration data.

        Returns
        -------
        Config
            The parsed configuration.
        """
        loader: ConfigLoader = self._config_loader_manager.get_or_create(config_source.content_type)
        return loader.load(config_source.read())

    def load_settings(self, settings_source: Source) -> Settings:
        """
        Load a `Settings` object from the given source.
        Ensures the configuration is a mapping (dict) before converting to `Settings`.

        Parameters
        ----------
        settings_source : Source
            The source containing settings data.

        Returns
        -------
        Settings
            The validated settings object.

        Raises
        ------
        SettingsConfigError
            If the loaded configuration is not a dictionary.
        """
          
        config: Config = self.load_config(settings_source)
        if not isinstance(config, dict):
            raise SettingsConfigError(config)
        
        return Settings.from_dict(config)