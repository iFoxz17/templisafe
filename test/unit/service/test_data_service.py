# test_data_service.py
from overrides import overrides
import pytest
from dataclasses import dataclass, is_dataclass
from unittest.mock import Mock

from templisafe.content.content import Content
from templisafe.service.data_service import DataService
from templisafe.service.source_service import SourceBundle
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

@dataclass(frozen=True)
class DummySourceBundle(SourceBundle):
    src3: Source
    src4: Source

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
def dummy_source3() -> Source:
    return Mock(spec=Source)

@pytest.fixture
def dummy_source4() -> Source:
    return Mock(spec=Source)

@pytest.fixture
def dummy_task_bundle(dummy_source1, dummy_source2) -> DummyTaskBundle:
    return DummyTaskBundle(src1=dummy_source1, src2=dummy_source2)

@pytest.fixture
def dummy_source_bundle(dummy_source3, dummy_source4) -> DummySourceBundle:
    return DummySourceBundle(src3=dummy_source3, src4=dummy_source4)

@pytest.fixture
def mock_field_selector(dummy_source1, dummy_source2) -> Mock:
    m = Mock(spec=FieldSelector)
    m.select_by_type.return_value = {
        "src1": dummy_source1,
        "src2": dummy_source2,
    }
    return m

@pytest.fixture
def mock_content_provider() -> Mock:
    m = Mock()
    # Produce dummy Content objects
    dummy_content1 = Mock(spec=Content)
    dummy_content2 = Mock(spec=Content)
    dummy_content3 = Mock(spec=Content)
    dummy_content4 = Mock(spec=Content)
    m.provide.return_value = Mock(
        contents=[
            ("src1", dummy_content1),
            ("src2", dummy_content2),
            ("src3", dummy_content3),
            ("src4", dummy_content4),
        ]
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
    dummy_source_bundle: DummySourceBundle
):
    bundle = data_service.process(dummy_task_bundle, dummy_source_bundle)

    # Check result is a dataclass
    assert is_dataclass(bundle)
    # Check all fields from content_group are present
    field_names = [f.name for f in bundle.__dataclass_fields__.values()]
    assert set(field_names) == {"src1", "src2", "src3", "src4"}

def test_data_service_calls_providers_correctly(
    data_service: DataService,
    dummy_task_bundle: DummyTaskBundle,
    dummy_source_bundle: DummySourceBundle,
    mock_field_selector: Mock,
    mock_content_provider: Mock
):
    _ = data_service.process(dummy_task_bundle, dummy_source_bundle)

    # FieldSelector is called once with task_bundle and Source type
    mock_field_selector.select_by_type.assert_called_once_with(dummy_task_bundle, types=Source)

    # ContentProvider is called once
    assert mock_content_provider.provide.call_count == 1
    args, kwargs = mock_content_provider.provide.call_args
    assert "source_group" in kwargs
    assert isinstance(kwargs["source_group"], object)  # could refine further