from typing import ClassVar
from unittest.mock import Mock

import pytest

from templisafe.content.content import Content, ContentType
from templisafe.core.task import TaskBundle, TaskType
from templisafe.service.data_service import DataService
from templisafe.service.field_selector import FieldSelector
from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.source.inline_source import InlineSource
from templisafe.source.source import Source


class DummyTaskBundle(TaskBundle):
    _type: ClassVar[TaskType] = TaskType.BUILD

    src1: Source
    src2: Source
    other_field: int = 42


@pytest.fixture
def dummy_source1() -> Source:
    return InlineSource(InlineSourceSettings(content_type=ContentType.TEXT, content="one"))


@pytest.fixture
def dummy_source2() -> Source:
    return InlineSource(InlineSourceSettings(content_type=ContentType.TEXT, content="two"))


@pytest.fixture
def dummy_task_bundle(dummy_source1, dummy_source2) -> DummyTaskBundle:
    return DummyTaskBundle(src1=dummy_source1, src2=dummy_source2)


@pytest.fixture
def mock_field_selector(dummy_source1, dummy_source2) -> Mock:
    selector = Mock(spec=FieldSelector)
    selector.select_by_type.return_value = {
        "src1": dummy_source1,
        "src2": dummy_source2,
    }
    return selector


@pytest.fixture
def mock_content_provider() -> Mock:
    provider = Mock()
    provider.provide.return_value = Mock(
        contents={
            "src1": Content("content-one", ContentType.TEXT),
            "src2": Content("content-two", ContentType.TEXT),
        }
    )
    return provider


@pytest.fixture
def data_service(
    mock_content_provider: Mock,
    mock_field_selector: Mock,
) -> DataService:
    return DataService(
        content_provider=mock_content_provider,
        field_selector=mock_field_selector,
    )


def test_data_service_process_updates_source_fields(
    data_service: DataService,
    dummy_task_bundle: DummyTaskBundle,
):
    bundle = data_service.process(dummy_task_bundle)

    assert isinstance(bundle, DummyTaskBundle)
    assert isinstance(bundle.src1, Content)
    assert isinstance(bundle.src2, Content)
    assert bundle.src1.payload == "content-one"
    assert bundle.src2.payload == "content-two"
    assert bundle.other_field == 42


def test_data_service_calls_providers_correctly(
    data_service: DataService,
    dummy_task_bundle: DummyTaskBundle,
    mock_field_selector: Mock,
    mock_content_provider: Mock,
):
    _ = data_service.process(dummy_task_bundle)

    mock_field_selector.select_by_type.assert_called_once_with(
        dummy_task_bundle,
        types=Source,
    )
    assert mock_content_provider.provide.call_count == 1
    _, kwargs = mock_content_provider.provide.call_args
    assert "source_group" in kwargs
    assert "source_executor" in kwargs
