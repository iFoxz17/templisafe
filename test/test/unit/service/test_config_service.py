import json
from typing import ClassVar
from unittest.mock import Mock

import pytest

from templisafe.content.content import Content, ContentType
from templisafe.core.field_selector import FieldSelector
from templisafe.parser.config.config_parser import ConfigParser
from templisafe.provider.config_parser_provider import ConfigParserProvider
from templisafe.provider.resource.resource_provider import ResourceProvider
from templisafe.service.config_service import ConfigService
from templisafe.task.task import TaskBundle, TaskType


class DummyDataBundle(TaskBundle):
    _type: ClassVar[TaskType] = TaskType.BUILD

    content1: Content
    content2: Content
    other_field: int = 99


@pytest.fixture
def dummy_content1() -> Content:
    return Content(payload='{"key": "value1"}', type_=ContentType.JSON)


@pytest.fixture
def dummy_content2() -> Content:
    return Content(payload='{"key": "value2"}', type_=ContentType.JSON)


@pytest.fixture
def dummy_data_bundle(dummy_content1, dummy_content2) -> DummyDataBundle:
    return DummyDataBundle(content1=dummy_content1, content2=dummy_content2)


@pytest.fixture
def mock_field_selector(dummy_content1, dummy_content2) -> Mock:
    selector = Mock(spec=FieldSelector)
    selector.select_by_type.return_value = {
        "content1": dummy_content1,
        "content2": dummy_content2,
    }
    return selector


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
def mock_resource_provider(mock_parser: Mock) -> Mock:
    provider = Mock(spec=ResourceProvider)
    provider.provide_config.side_effect = lambda payload, parser: parser.parse(payload)
    return provider


@pytest.fixture
def config_service(
    mock_config_parser_provider: Mock,
    mock_field_selector: Mock,
    mock_resource_provider: Mock,
) -> ConfigService:
    return ConfigService(
        config_parser_provider=mock_config_parser_provider,
        field_selector=mock_field_selector,
        resource_provider=mock_resource_provider,
    )


def test_config_service_process_updates_content_fields(
    config_service: ConfigService,
    dummy_data_bundle: DummyDataBundle,
):
    bundle = config_service.process(dummy_data_bundle)

    assert isinstance(bundle, DummyDataBundle)
    assert bundle.content1 == {"key": "value1"}
    assert bundle.content2 == {"key": "value2"}
    assert bundle.other_field == 99


def test_config_service_calls_provider_correctly(
    config_service: ConfigService,
    dummy_data_bundle: DummyDataBundle,
    mock_config_parser_provider: Mock,
    mock_resource_provider: Mock,
):
    _ = config_service.process(dummy_data_bundle)

    calls = mock_config_parser_provider.provide.call_args_list
    content_types = {dummy_data_bundle.content1.type_, dummy_data_bundle.content2.type_}
    called_types = {call.args[0] for call in calls}
    assert called_types == content_types
    assert mock_resource_provider.provide_config.call_count == 2
