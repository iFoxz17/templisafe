from typing import ClassVar
from unittest.mock import Mock

import pytest

from templisafe.content.content import ContentType
from templisafe.core.field_selector import FieldSelector
from templisafe.service.source_service import SourceService
from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.settings.source.source_settings import SourceSettings
from templisafe.source.inline_source import InlineSource
from templisafe.source.source import Source
from templisafe.task.task import TaskBundle, TaskType


class DummyTaskBundle(TaskBundle):
    _type: ClassVar[TaskType] = TaskType.BUILD

    template_source: Source
    variants_source: SourceSettings
    other_field: int = 42


@pytest.fixture
def dummy_settings() -> InlineSourceSettings:
    return InlineSourceSettings(content_type=ContentType.TEXT, content="variants")


@pytest.fixture
def dummy_source() -> InlineSource:
    return InlineSource(InlineSourceSettings(content_type=ContentType.TEXT, content="template"))


@pytest.fixture
def resolved_source() -> InlineSource:
    return InlineSource(InlineSourceSettings(content_type=ContentType.TEXT, content="resolved"))


@pytest.fixture
def dummy_task_bundle(
    dummy_source: InlineSource,
    dummy_settings: InlineSourceSettings,
) -> DummyTaskBundle:
    return DummyTaskBundle(
        template_source=dummy_source,
        variants_source=dummy_settings,
    )


@pytest.fixture
def mock_selector(
    dummy_source: InlineSource,
    dummy_settings: InlineSourceSettings,
) -> Mock:
    selector = Mock(spec=FieldSelector)
    selector.select_by_type.return_value = {
        "template_source": dummy_source,
        "variants_source": dummy_settings,
    }
    return selector


@pytest.fixture
def mock_provider(resolved_source: InlineSource) -> Mock:
    provider = Mock()
    provider.provide.side_effect = lambda x: x if isinstance(x, Source) else resolved_source
    return provider


@pytest.fixture
def source_service(mock_provider: Mock, mock_selector: Mock) -> SourceService:
    return SourceService(
        source_provider=mock_provider,
        field_selector=mock_selector,
    )


def test_source_service_process_resolves_source_settings(
    source_service: SourceService,
    dummy_task_bundle: DummyTaskBundle,
    dummy_source: InlineSource,
    resolved_source: InlineSource,
) -> None:
    bundle = source_service.process(dummy_task_bundle)

    assert isinstance(bundle, DummyTaskBundle)
    assert bundle.template_source is dummy_source
    assert bundle.variants_source is resolved_source
    assert bundle.other_field == 42
    source_service._field_selector.select_by_type.assert_called_once_with(  # type: ignore[attr-defined]
        obj=dummy_task_bundle,
        types=(Source, SourceSettings),
    )
    assert source_service._source_provider.provide.call_count == 2  # type: ignore[attr-defined]
