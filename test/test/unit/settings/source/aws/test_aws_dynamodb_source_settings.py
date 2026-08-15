import json

import pytest

from templisafe.exceptions.settings_error import SettingsError
from templisafe.settings.source.aws.aws_dynamodb_source_settings import (
    AwsDynamoDBSourceSettings,
)
from templisafe.settings.source.source_settings import SourceKind, SourceSettings

# -----------------------------
# Example configs
# -----------------------------
DYNAMODB_CONFIG_DICT = {
    "kind": "aws_dynamodb",
    "table_name": "my-table",
    "key": {"id": "123"},
    "projection_expression": "username",
    "aws_access_key_id": "AKIAFAKE",
    "aws_secret_access_key": "SECRETFAKE",
    "region_name": "us-east-1",
    "endpoint_url": "http://localhost:4566",
}

DYNAMODB_JSON = json.dumps({**DYNAMODB_CONFIG_DICT})


# -----------------------------
# Tests for creation
# -----------------------------
def test_create_dynamodb_only_required():
    instance = AwsDynamoDBSourceSettings(table_name="my-table", key=(("id", "123"),))
    assert isinstance(instance, AwsDynamoDBSourceSettings)
    assert instance.kind == SourceKind.AWS_DYNAMODB
    assert instance.table_name == "my-table"
    assert instance.key == (("id", "123"),)
    assert instance.key_dict == {"id": "123"}
    assert instance.projection_expression is None


def test_create_dynamodb_from_dict():
    instance = SourceSettings.create(**DYNAMODB_CONFIG_DICT)
    assert isinstance(instance, AwsDynamoDBSourceSettings)
    assert instance.kind == SourceKind.AWS_DYNAMODB
    assert instance.table_name == "my-table"
    assert instance.key == (("id", "123"),)
    assert instance.key_dict == {"id": "123"}
    assert instance.projection_expression == "username"
    assert instance.aws_access_key_id == "AKIAFAKE"
    assert instance.aws_secret_access_key == "SECRETFAKE"
    assert instance.region_name == "us-east-1"
    assert instance.endpoint_url == "http://localhost:4566"


def test_create_missing_required_field_raises():
    cfg = DYNAMODB_CONFIG_DICT.copy()
    cfg.pop("table_name")
    with pytest.raises(ValueError, match="Invalid fields"):
        SourceSettings.create(**cfg)


def test_create_extra_field_raises():
    cfg = DYNAMODB_CONFIG_DICT.copy()
    cfg["extra"] = 123  # type: ignore
    with pytest.raises(ValueError):
        SourceSettings.create(**cfg)


def test_from_dict_dynamodb():
    instance = AwsDynamoDBSourceSettings.from_dict(DYNAMODB_CONFIG_DICT)
    assert isinstance(instance, AwsDynamoDBSourceSettings)
    assert instance.table_name == "my-table"
    assert instance.key == (("id", "123"),)


def test_from_json_dynamodb():
    instance = AwsDynamoDBSourceSettings.from_json(DYNAMODB_JSON)
    assert isinstance(instance, AwsDynamoDBSourceSettings)
    assert instance.table_name == "my-table"
    # key will need conversion from list to tuple for JSON tests
    key_dict = json.loads(DYNAMODB_JSON)["key"]
    assert instance.key_dict == key_dict
