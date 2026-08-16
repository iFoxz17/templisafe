SCHEMA_PARSER_SETTINGS_YAML: str = """
schema_key: schema
type_key: type
default_key: default
constraints_key: constraints
metadata_key: metadata
index_key: _index
model_name: ModelSchema
allowed_types: [bool, int, float, str, optional, list, dict, date, datetime, object]
type_aliases:
  bool: [boolean]
  int: [integer]
  float: [real, number]
  str: [string]
  object: [any]
"""
