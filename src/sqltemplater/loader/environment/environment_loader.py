import yaml
from jinja2 import Environment

from sqltemplater.settings.environment_settings import EnvironmentSettings
from sqltemplater.loader.environment.environment_manager import EnvironmentManager
from sqltemplater.source.source import Source
from sqltemplater.source.inline_source import InlineSource
from sqltemplater.settings.source_settings import InlineSourceSettings
from sqltemplater.util.util import ContentType
from sqltemplater.exceptions.environment_error import IllegalEnvironmentDefinitionError

ENV_PARSER_SETTINGS: str = """
optimized: true
"""

class EnvironmentLoader:
    """Loads and manages Jinja2 environments from configuration sources."""

    __slots__: tuple[str, ...] = ("_default_settings", "_default_settings_source", "_manager")

    @staticmethod
    def _get_default_settings_source() -> InlineSource:
        settings: InlineSourceSettings = InlineSourceSettings(
            content_type=ContentType.YAML, 
            content=ENV_PARSER_SETTINGS
            )
        return InlineSource(settings)

    def __init__(self, default_settings_source: Source | None = None) -> None:
        self._default_settings_source: Source = (
            default_settings_source or 
            EnvironmentLoader._get_default_settings_source()
        )
        self._default_settings: EnvironmentSettings = self._load_env_settings(self._default_settings_source)
        self._manager: EnvironmentManager = EnvironmentManager()

    def _load_env_settings(self, settings_source: Source) -> EnvironmentSettings:
        raw: str = settings_source.read()
        try:
            data = yaml.safe_load(raw) or {}
        except yaml.YAMLError as e:
            raise IllegalEnvironmentDefinitionError(
                f"Failed to parse environment YAML config: {e}"
            ) from e

        if not isinstance(data, dict):
            raise IllegalEnvironmentDefinitionError(
                "Environment configuration must contain a mapping at top level"
            )

        try:
            return EnvironmentSettings(**data)
        except Exception as e:
            raise IllegalEnvironmentDefinitionError(
                f"Invalid environment configuration: {e}"
            ) from e

    def _create_settings(self, env_settings_source: Source | None = None) -> EnvironmentSettings:
        env_settings: EnvironmentSettings
        if env_settings_source is None:
            env_settings = self._default_settings
        else:
            env_settings = self._load_env_settings(env_settings_source)
        
        assert isinstance(env_settings, EnvironmentSettings)
        return env_settings

    def load(self, env_settings_source: Source | None = None) -> Environment:
        env_settings: EnvironmentSettings = self._create_settings(env_settings_source)
        return self._manager.get_or_create(env_settings)