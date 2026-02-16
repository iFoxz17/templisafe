from overrides import overrides
import pytest
from dataclasses import dataclass, is_dataclass, fields
from unittest.mock import Mock

from templisafe.content.content import Content
from templisafe.service.data_service import DataService
from templisafe.service.field_selector import FieldSelector
from templisafe.settings.source_executor_settings import SourceExecutorSettings
from templisafe.source.source import Source
from templisafe.task import TaskBundle, TaskType

# ------------------------------
# Dummy task bundle and sources
# ------------------------------
@dataclass(frozen=True)
class DummyTaskBundle(TaskBundle):
    src1: Source
    src2: Source
    other_field: int = 42

    @property
    @overrides
    def type_(self) -> TaskType:
        return TaskType.BUILD

# ------------------------------
# Fixtures
# ------------------------------
@pytest.fixture
def dummy_source1() -> Source:
    return Mock(spec=Source)

@pytest.fixture
def dummy_source2() -> Source:
    return Mock(spec=Source)

@pytest.fixture
def dummy_task_bundle(dummy_source1, dummy_source2) -> DummyTaskBundle:
    return DummyTaskBundle(src1=dummy_source1, src2=dummy_source2)

@pytest.fixture
def mock_field_selector(dummy_source1, dummy_source2) -> Mock:
    m = Mock(spec=FieldSelector)
    # Select only Source fields from the task bundle
    m.select_by_type.return_value = {
        "src1": dummy_source1,
        "src2": dummy_source2,
    }
    return m

@pytest.fixture
def mock_content_provider() -> Mock:
    m = Mock()
    # Produce dummy Content objects for each source field
    dummy_content1 = Mock(spec=Content)
    dummy_content2 = Mock(spec=Content)
    m.provide.return_value = Mock(
        contents={
            "src1": dummy_content1,
            "src2": dummy_content2,
        }
    )
    return m

@pytest.fixture
def data_service(mock_content_provider: Mock, mock_field_selector: Mock) -> DataService:
    return DataService(
        content_provider=mock_content_provider,
        field_selector=mock_field_selector
    )

# ------------------------------
# Tests
# ------------------------------
def test_data_service_process_creates_databundle(
    data_service: DataService,
    dummy_task_bundle: DummyTaskBundle,
):
    bundle = data_service.process(dummy_task_bundle)
    assert isinstance(bundle, DummyTaskBundle)

    # Check result is a dataclass
    assert is_dataclass(bundle)

    # Check all fields from content_group are present
    field_names = [f.name for f in fields(bundle)]
    assert set(field_names) == {f.name for f in fields(dummy_task_bundle)}

    # Check resolved fields are Content instances
    assert isinstance(getattr(bundle, "src1"), Content)
    assert isinstance(getattr(bundle, "src2"), Content)

    # Unresolved fields retain original values
    assert getattr(bundle, "other_field") == 42

def test_data_service_calls_providers_correctly(
    data_service: DataService,
    dummy_task_bundle: DummyTaskBundle,
    mock_field_selector: Mock,
    mock_content_provider: Mock
):
    _ = data_service.process(dummy_task_bundle)

    # FieldSelector is called once with task_bundle and Source type
    mock_field_selector.select_by_type.assert_called_once_with(dummy_task_bundle, types=Source)

    # ContentProvider is called once with SourceGroup and optional executor
    assert mock_content_provider.provide.call_count == 1
    args, kwargs = mock_content_provider.provide.call_args
    assert "source_group" in kwargs
    assert isinstance(kwargs["source_group"], object)  # could refine further
    assert "source_executor" in kwargs