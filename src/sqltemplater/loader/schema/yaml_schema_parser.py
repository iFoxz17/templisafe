import yaml
from overrides import overrides
from typing import Any

from sqltemplater.settings.parser.schema_parser_settings import YamlSchemaParserSettings
from sqltemplater.exceptions.schema_error import IllegalSchemaError
from sqltemplater.loader.schema.schema_parser import SchemaParser

class YamlSchemaParser(SchemaParser):

    def __init__(self, settings: YamlSchemaParserSettings) -> None:
        super().__init__(settings)

    @overrides
    def _parse_raw(self, schema: str) -> dict[str, Any]:
        """
        Parse a YAML string into a dictionary.

        Args:
            schema: YAML string representing the schema.

        Returns:
            A dictionary mapping the top-level schema key to parameter definitions.

        Raises:
            IllegalSchemaError: If the YAML cannot be parsed or is invalid.
        """
        try:
            data: Any = yaml.safe_load(schema)
        except yaml.YAMLError as e:
            raise IllegalSchemaError(f"Failed to parse YAML: {e}") from e

        if not isinstance(data, dict):
            raise IllegalSchemaError("Parsed YAML schema is not a dictionary")

        return data