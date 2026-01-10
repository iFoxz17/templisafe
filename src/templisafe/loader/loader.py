from abc import ABC, abstractmethod
import yaml
from typing import Any
from dataclasses import dataclass

from templisafe.source.source import Source
from templisafe.util.util import DiagnosticPolicy, ContentType
from templisafe.settings.parser.parser_settings import ParserSettings

@dataclass(frozen=True, slots=True)
class LoaderContext(ABC):
    """Base class representing the context in which a loader operates."""
    pass

class Loader(ABC):
    """Abstract base class for loaders that parse and manage configuration sources."""

    __slots__: tuple[str, ...] = ('_default_settings_source', '_default_settings')

    _PARSER_TYPE_KEY: str = 'parser_type'
    _DEFAULT_POLICY_KEY: str = 'default_diagnostic_policy'

    def __init__(self, default_settings_source: Source) -> None:
        self._default_settings_source: Source = default_settings_source
        self._default_settings: ParserSettings = self._load_parser_settings(default_settings_source)
        
    @abstractmethod
    def _load_parser_settings(self, settings_source: Source, context: LoaderContext | None = None) -> ParserSettings:
        pass

    def _load_config(self, raw: str, error_type: type[Exception]) -> dict[str, Any]:
        try:
            config = yaml.safe_load(raw) or {}
        except yaml.YAMLError as e:
            raise error_type(f"Failed to parse YAML config: {e}") from e

        if not isinstance(config, dict):
            raise error_type("Schema configuration file must contain an object at top level")
        
        return config

    def _load_parser_type(self, config: dict[str, Any], error_type: type[Exception]) -> ContentType:
        parser_type: ContentType
        key: str = self._PARSER_TYPE_KEY 
        if key not in config:
            raise error_type(f"No parser type found: define a value for key '{key}'")
        parser_type_str: str = config[key]
        try:
            parser_type = ContentType[parser_type_str]
        except KeyError:
            raise error_type(f"Invalid parser type value: {parser_type_str}")

        return parser_type

    def _load_diagnostic_policy(self, config: dict[str, Any], error_type: type[Exception]) -> DiagnosticPolicy:       
        policy: DiagnosticPolicy
        key: str = self._DEFAULT_POLICY_KEY 
        if key in config:
            policy_str: str = config[key]
            try:
                policy = DiagnosticPolicy[policy_str]
            except KeyError:
                raise error_type(f"Invalid policy value: {policy_str}")
        else:
            policy = DiagnosticPolicy.RAISE_WARNINGS

        return policy