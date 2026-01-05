import yaml
from overrides import overrides
from typing import Any

from sqltemplater.settings.parser.params_parser_settings import YamlParamsParserSettings
from sqltemplater.exceptions.params_error import IllegalParamsError
from sqltemplater.loader.params.params_parser import ParamsParser

class YamlParamsParser(ParamsParser):

    def __init__(self, settings: YamlParamsParserSettings) -> None:
        super().__init__(settings)

    @overrides
    def _parse_raw(self, params: str) -> dict[str, Any]:
        """
        Parse a YAML string into a dictionary.

        Args:
            params: YAML string representing the params.

        Returns:
            A dictionary mapping the top-level params key to parameter definitions.

        Raises:
            IllegalParamsError: If the YAML cannot be parsed or is invalid.
        """
        try:
            data: Any = yaml.safe_load(params)
        except yaml.YAMLError as e:
            raise IllegalParamsError(f"Failed to parse YAML: {e}") from e

        if not isinstance(data, dict):
            raise IllegalParamsError("Parsed YAML params is not a dictionary")

        return data