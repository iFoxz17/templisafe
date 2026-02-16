from overrides import overrides
import pytest
from dataclasses import dataclass, is_dataclass, fields
from unittest.mock import Mock

from templisafe.content.content import ContentType
from templisafe.service.field_selector import FieldSelector
from templisafe.service.source_service import SourceService
from templisafe.task import TaskBundle, TaskType
from templisafe.source.source import Source
from templisafe.settings.source.source_settings import SourceKind, SourceSettings

# ------------------------------
# Dummy source classes
# ------------------------------
class DummySourceSettings(SourceSettings):
    @property
    @overrides
    def kind(self) -> SourceKind:
        return SourceKind.CUSTOM

class DummySource(Source):
    @overrides
    def read(self) -> str:
        return "Hello world!"

# ------------------------------
# Dummy task bundle for testing
# ------------------------------
@dataclass(frozen=True)
class DummyTaskBundle(TaskBundle):
    template_source: Source
    compiler_settings: SourceSettings
    other_field: int = 42

    @property
    def type_(self):
        return TaskType.BUILD

# ------------------------------
# Pytest fixtures
# ------------------------------
@pytest.fixture
def dummy_settings() -> DummySourceSettings:
    return DummySourceSettings(content_type=ContentType.TEXT)

@pytest.fixture
def dummy_source(dummy_settings: DummySourceSettings) -> DummySource:
    return DummySource(dummy_settings)

@pytest.fixture
def dummy_task_bundle(dummy_source: DummySource, dummy_settings: DummySourceSettings) -> DummyTaskBundle:
    return DummyTaskBundle(template_source=dummy_source, compiler_settings=dummy_settings)

@pytest.fixture
def mock_selector(dummy_source: DummySource, dummy_settings: DummySourceSettings) -> FieldSelector:
    """Mock FieldSelector that returns fields to be resolved."""
    selector = Mock(spec=FieldSelector)
    selector.select_by_type.return_value = {
        "template_source": dummy_source,
        "compiler_settings": dummy_settings,
    }
    return selector

@pytest.fixture
def mock_provider() -> Mock:
    """Mock SourceProvider as identity."""
    provider = Mock()
    provider.provide.side_effect = lambda x: x
    return provider

@pytest.fixture
def source_service(mock_provider: Mock, mock_selector: FieldSelector) -> SourceService:
    return SourceService(source_provider=mock_provider, field_selector=mock_selector)

# ------------------------------
# Tests
# ------------------------------
def test_source_service_process_creates_bundle(
    source_service: SourceService, 
    dummy_task_bundle: DummyTaskBundle, 
    dummy_source: DummySource, 
    dummy_settings: DummySourceSettings
) -> None:
    bundle: TaskBundle = source_service.process(dummy_task_bundle)
    assert isinstance(bundle, DummyTaskBundle)

    # Check it is a dataclass
    assert is_dataclass(bundle)

    # All fields exist in the dynamically generated bundle
    bundle_field_names = [f.name for f in fields(bundle)]
    assert set(bundle_field_names) == set([f.name for f in fields(dummy_task_bundle)])

    # Resolved fields are narrowed to Source
    assert isinstance(bundle.template_source, Source)
    assert isinstance(bundle.compiler_settings, SourceSettings)

    # Values match what FieldProvider returned
    assert bundle.template_source is dummy_source
    assert bundle.compiler_settings is dummy_settings

    # Unresolved field retains original value
    assert bundle.other_field == 42

    # Verify mocks were called
    source_service._field_selector.select_by_type.assert_called_once_with(      # type: ignore
        obj=dummy_task_bundle,
        types=(Source, SourceSettings)
    )
    # Provider was used for each resolved field
    assert source_service._source_provider.provide.call_count == 2              # type: ignore