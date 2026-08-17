import json

import boto3
import pytest
from moto import mock_aws

from templisafe.content.content import ContentType
from templisafe.exceptions.source_error import AwsSourceError
from templisafe.settings.source.aws.aws_dynamodb_source_settings import (
    AwsDynamoDBSourceSettings,
)
from templisafe.source.aws.aws_dynamodb_source import AwsDynamoDBSource

# -----------------------------
# Constants
# -----------------------------
TEST_TABLE = "my-table"
TEST_KEY = (("id", "123"),)
TEST_ITEM = {"id": "123", "username": "admin", "password": "secret"}


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def dynamodb_settings() -> AwsDynamoDBSourceSettings:
    return AwsDynamoDBSourceSettings(
        content_type=ContentType.TEXT,
        table_name=TEST_TABLE,
        key=TEST_KEY,
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
    )


@pytest.fixture
def moto_dynamodb():
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName=TEST_TABLE,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        client.put_item(TableName=TEST_TABLE, Item={k: {"S": v} for k, v in TEST_ITEM.items()})
        yield


# -----------------------------
# Tests
# -----------------------------
def test_read_returns_item(moto_dynamodb, dynamodb_settings):
    source = AwsDynamoDBSource(dynamodb_settings)
    content = source.read()
    item = json.loads(content)
    assert item == TEST_ITEM


def test_read_raises_on_missing_item(moto_dynamodb):
    settings = AwsDynamoDBSourceSettings(
        content_type=ContentType.TEXT,
        table_name=TEST_TABLE,
        key=(("id", "missing"),),
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
    )
    source = AwsDynamoDBSource(settings)
    with pytest.raises(AwsSourceError):
        source.read()


def test_read_with_projection_expression(moto_dynamodb):
    settings = AwsDynamoDBSourceSettings(
        content_type=ContentType.TEXT,
        table_name=TEST_TABLE,
        key=TEST_KEY,
        projection_expression="username",
        aws_access_key_id="FAKE_KEY",
        aws_secret_access_key="FAKE_SECRET",
        region_name="us-east-1",
    )
    source = AwsDynamoDBSource(settings)
    content = source.read()
    item = json.loads(content)
    assert item == {"username": "admin"}
