import yaml
from overrides import overrides
from typing import Any

from sqltemplater.settings.parser.schema_parser_settings import YamlSchemaParserSettings
from sqltemplater.exceptions.schema_error import IllegalSchemaError
from sqltemplater.loader.schema.schema_parser import SchemaParser

class YamlSchemaParser(SchemaParser):
    """Parses a YAML schema string into a structured dictionary."""

    __slots__: tuple[str, ...] = ()

    def __init__(self, settings: YamlSchemaParserSettings) -> None:
        super().__init__(settings)

    @overrides
    def _parse_raw(self, schema: str) -> dict[str, Any]:
        """Parse a YAML schema string into a dictionary of parameter definitions."""

        try:
            data: Any = yaml.safe_load(schema)
        except yaml.YAMLError as e:
            raise IllegalSchemaError(f"Failed to parse YAML: {e}") from e

        if not isinstance(data, dict):
            raise IllegalSchemaError("Parsed YAML schema is not a dictionary")

        return data