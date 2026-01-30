from pydantic import BaseModel
import pytest
from unittest.mock import Mock

from templisafe.parser.config.config_parser import Config
from templisafe.parser.schema.schema_parser import Schema, SchemaParser
from templisafe.provider.resource.schema_provider import SchemaProvider


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def provider() -> SchemaProvider:
    """Return a SchemaProvider instance."""
    return SchemaProvider()


@pytest.fixture
def config() -> Config:
    """Return a basic Config instance."""
    return {"field_a": "type1", "field_b": "type2"}


class DummySchema(BaseModel):
    pass

@pytest.fixture
def parser() -> SchemaParser:
    """Return a mocked SchemaParser."""
    parser_mock = Mock(spec=SchemaParser)
    parser_mock.parse.return_value = Schema(DummySchema)
    return parser_mock


# -----------------------------
# Tests
# -----------------------------
def test_provide_returns_schema(provider: SchemaProvider, config: Config, parser: Mock):
    """Provider delegates parsing to the SchemaParser and returns a Schema."""
    result = provider.provide(config, parser)

    # Verify return type and content
    assert isinstance(result, Schema)
    assert result == parser.parse.return_value

    # Verify parser was called with the config
    parser.parse.assert_called_once_with(config)
