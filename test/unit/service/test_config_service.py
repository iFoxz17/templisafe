# test_config_service.py
from dataclasses import dataclass, fields, is_dataclass
import json
from unittest.mock import Mock
import pytest

from templisafe.content.content import Content, ContentType
from templisafe.parser.config.config_parser import Config, ConfigParser
from templisafe.provider.config_parser_provider import ConfigParserProvider
from templisafe.service.field_selector import FieldSelector
from templisafe.service.config_service import ConfigService
from templisafe.task import TaskBundle, TaskType

# ------------------------------
# Dummy TaskBundle
# ------------------------------
@dataclass(frozen=True)
class DummyDataBundle(TaskBundle):
    content1: Content
    content2: Content
    other_field: int = 99

    @property
    def type_(self) -> TaskType:
        return TaskType.BUILD

# ------------------------------
# Fixtures
# ------------------------------
@pytest.fixture
def dummy_content1() -> Content:
    return Content(
        payload='{"key": "value1"}',
        type_=ContentType.JSON
    )

@pytest.fixture
def dummy_content2() -> Content:
    return Content(
        payload='{"key": "value2"}',
        type_=ContentType.JSON
    )


@pytest.fixture
def dummy_data_bundle(dummy_content1, dummy_content2) -> DummyDataBundle:
    return DummyDataBundle(content1=dummy_content1, content2=dummy_content2)

@pytest.fixture
def mock_field_selector(dummy_content1, dummy_content2) -> Mock:
    # Not used in current ConfigService, but kept for consistency

    m = Mock()
    # Produce dummy Content objects for each source field
    m.select_by_type.return_value = {
        "content1": dummy_content1,
        "content2": dummy_content2,
    }
    return m

@pytest.fixture
def mock_parser() -> Mock:
    parser = Mock(spec=ConfigParser)
    parser.parse.side_effect = lambda payload: json.loads(payload)
    return parser

@pytest.fixture
def mock_config_parser_provider(mock_parser: Mock) -> Mock:
    provider = Mock(spec=ConfigParserProvider)
    provider.provide.return_value = mock_parser
    return provider

@pytest.fixture
def config_service(mock_config_parser_provider: Mock, mock_field_selector: Mock) -> ConfigService:
    return ConfigService(
        config_parser_provider=mock_config_parser_provider,
        field_selector=mock_field_selector
    )

# ------------------------------
# Tests
# ------------------------------
def test_config_service_process_creates_configbundle(
    config_service: ConfigService,
    dummy_data_bundle: DummyDataBundle
):
    bundle = config_service.process(dummy_data_bundle)
    assert isinstance(bundle, DummyDataBundle)

    # Should be a dataclass
    assert is_dataclass(bundle)

    # All fields are present
    field_names = [f.name for f in fields(bundle)]
    assert set(field_names) == {f.name for f in fields(dummy_data_bundle)}

    # Resolved fields are dict (Config)
    assert isinstance(getattr(bundle, "content1"), dict)
    assert isinstance(getattr(bundle, "content2"), dict)

    # Pass-through field remains unchanged
    assert getattr(bundle, "other_field") == 99

def test_config_service_calls_provider_correctly(
    config_service: ConfigService,
    dummy_data_bundle: DummyDataBundle,
    mock_config_parser_provider: Mock
):
    _ = config_service.process(dummy_data_bundle)

    # Provider called for each unique ContentType
    calls = mock_config_parser_provider.provide.call_args_list
    content_types = {dummy_data_bundle.content1.type_, dummy_data_bundle.content2.type_}
    called_types = {call.args[0] for call in calls}
    assert called_types == content_types