from typing import Annotated, ClassVar
from unittest.mock import Mock

import pytest
from pydantic import Field

from templisafe.core.field_selector import FieldSelector
from templisafe.parser.settings.settings_parser import SettingsParser
from templisafe.provider.resource.resource_provider import ResourceProvider
from templisafe.provider.settings_parser_provider import SettingsParserProvider
from templisafe.service.settings_service import SettingsService
from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.settings import SettingsKind
from templisafe.task.task import CategoryMetadata, FieldCategory, TaskBundle, TaskType


class DummySettingsBundle(TaskBundle):
    _type: ClassVar[TaskType] = TaskType.BUILD

    compiler_settings: Annotated[
        dict[str, str],
        Field(default=...),
        CategoryMetadata(FieldCategory.COMPONENT),
    ]


@pytest.fixture
def mock_settings_parser() -> Mock:
    return Mock(spec=SettingsParser)


@pytest.fixture
def mock_settings_parser_provider(mock_settings_parser: Mock) -> Mock:
    provider = Mock(spec=SettingsParserProvider)
    provider.provide.return_value = mock_settings_parser
    return provider


@pytest.fixture
def mock_resource_provider() -> Mock:
    provider = Mock(spec=ResourceProvider)
    provider.provide_settings.return_value = CompilerSettings(index_key="custom_index")
    return provider


@pytest.fixture
def settings_service(
    mock_settings_parser_provider: Mock,
    mock_resource_provider: Mock,
) -> SettingsService:
    return SettingsService(
        settings_parser_provider=mock_settings_parser_provider,
        field_selector=Mock(spec=FieldSelector),
        resource_provider=mock_resource_provider,
    )


def test_settings_service_delegates_settings_creation_to_resource_provider(
    settings_service: SettingsService,
    mock_settings_parser_provider: Mock,
    mock_settings_parser: Mock,
    mock_resource_provider: Mock,
):
    bundle = DummySettingsBundle(compiler_settings={"index_key": "custom_index"})

    result = settings_service.process(bundle)

    assert result.compiler_settings == CompilerSettings(index_key="custom_index")
    mock_settings_parser_provider.provide.assert_called_once_with(SettingsKind.COMPILER_SETTINGS)
    mock_resource_provider.provide_settings.assert_called_once_with(
        {"kind": SettingsKind.COMPILER_SETTINGS.value, "index_key": "custom_index"},
        mock_settings_parser,
    )


def test_settings_service_respects_explicit_settings_kind(
    settings_service: SettingsService,
    mock_settings_parser_provider: Mock,
    mock_settings_parser: Mock,
    mock_resource_provider: Mock,
):
    bundle = DummySettingsBundle(compiler_settings={"kind": "compiler_settings", "index_key": "custom_index"})

    result = settings_service.process(bundle)

    assert result.compiler_settings == CompilerSettings(index_key="custom_index")
    mock_settings_parser_provider.provide.assert_called_once_with(SettingsKind.COMPILER_SETTINGS)
    mock_resource_provider.provide_settings.assert_called_once_with(
        {"kind": "compiler_settings", "index_key": "custom_index"},
        mock_settings_parser,
    )
