import json
from typing import Any

from overrides import overrides

from templisafe.exceptions.source_error import AwsSourceError
from templisafe.settings.source.aws.aws_dynamodb_source_settings import (
    AwsDynamoDBSourceSettings,
)
from templisafe.settings.source.aws.aws_source_settings import AwsSourceSettings
from templisafe.source.aws.aws_source import AwsSource


class AwsDynamoDBSource(AwsSource):
    """Reads an item from DynamoDB lazily, only connecting on read()."""

    def __init__(self, settings: AwsDynamoDBSourceSettings) -> None:
        super().__init__(settings)

    @property
    def table_name(self) -> str:
        assert isinstance(self._settings, AwsDynamoDBSourceSettings)
        return self._settings.table_name

    @property
    def key(self) -> tuple[tuple[str, str], ...]:
        assert isinstance(self._settings, AwsDynamoDBSourceSettings)
        return self._settings.key

    @property
    def projection_expression(self) -> str | None:
        assert isinstance(self._settings, AwsDynamoDBSourceSettings)
        return self._settings.projection_expression

    @overrides
    def read(self) -> str:
        client: Any = self._get_client("dynamodb")
        ClientError = self._client_error_type()
        settings: AwsSourceSettings = self.settings
        assert isinstance(settings, AwsDynamoDBSourceSettings)

        try:
            kwargs: dict[str, Any] = {
                "TableName": settings.table_name,
                "Key": {k: {"S": v} for k, v in settings.key},
            }
            if settings.projection_expression:
                kwargs["ProjectionExpression"] = settings.projection_expression

            resp = client.get_item(**kwargs)
            item = resp.get("Item")
            if item is None:
                raise AwsSourceError(f"Item {dict(settings.key)} not found in table {settings.table_name}")

            # Convert DynamoDB format {"S": "value"} -> plain dict
            result = {k: list(v.values())[0] for k, v in item.items()}

            # Return as JSON string
            return json.dumps(result)

        except ClientError as e:
            raise AwsSourceError(f"Failed to read item {dict(settings.key)} from table {settings.table_name}") from e
