import time
import pytest
from typing import Any

from templisafe.loader.source_loader import SourceLoader, SourceLoadInput, SourceLoaderSettings
from templisafe.source.source import Source
from templisafe.settings.settings import Settings


# --- Mock Sources ---
class DummySource(Source):
    def __init__(self, value: Any):
        self.value = value

    def read(self) -> str:
        return str(self.value)


class SlowSource(Source):
    """Simulates a slow read to test concurrency."""
    def __init__(self, value: Any, delay: float = 0.1):
        self.value = value
        self.delay = delay

    def read(self) -> str:
        time.sleep(self.delay)
        return str(self.value)


# --- Mock ConfigLoader ---
class DummyConfigLoader:
    """Mocks the ConfigLoader behavior."""
    def load_config(self, source: Source) -> dict[str, Any]:
        return {"config": source.read()}

    def load_settings(self, source: Source) -> Settings:
        return Settings()


# --- Fixtures ---
@pytest.fixture
def config_loader():
    return DummyConfigLoader()


@pytest.fixture
def serial_sources():
    """Sources for serial load test."""
    return SourceLoadInput(
        template_source=DummySource("template"),
        schema_source=DummySource("schema"),
        variants_sources=[DummySource(f"variant{i}") for i in range(3)],
        template_engine_settings_source=DummySource("engine_settings"),
        template_parser_settings_source=DummySource("parser_settings"),
        schema_parser_settings_source=DummySource("schema_parser"),
        variant_parser_settings_source=DummySource("variant_parser"),
        compiler_settings_source=DummySource("compiler"),
        renderer_settings_source=DummySource("renderer"),
    )


@pytest.fixture
def concurrent_sources():
    """Sources for concurrent load test with slow sources."""
    return SourceLoadInput(
        template_source=SlowSource("template", delay=0.05),
        schema_source=SlowSource("schema", delay=0.05),
        variants_sources=[SlowSource(f"variant{i}", delay=0.05) for i in range(4)],
        template_engine_settings_source=SlowSource("engine_settings", delay=0.05),
        template_parser_settings_source=SlowSource("parser_settings", delay=0.05),
        schema_parser_settings_source=SlowSource("schema_parser", delay=0.05),
        variant_parser_settings_source=SlowSource("variant_parser", delay=0.05),
        compiler_settings_source=SlowSource("compiler", delay=0.05),
        renderer_settings_source=SlowSource("renderer", delay=0.05),
    )


def test_load_serial(serial_sources, config_loader):
    loader = SourceLoader(SourceLoaderSettings(concurrent=False), config_loader=config_loader)
    output = loader.load(serial_sources)

    assert output.template_str == "template"
    assert output.schema_config == {"config": "schema"}
    assert [v["config"] for v in output.variants_configs] == ["variant0", "variant1", "variant2"]       # type: ignore
    assert isinstance(output.template_engine_settings, Settings)
    assert isinstance(output.template_parser_settings, str)
    assert isinstance(output.schema_parser_settings_source, str)
    assert isinstance(output.variant_parser_settings_source, str)
    assert isinstance(output.compiler_settings_source, str)
    assert isinstance(output.renderer_settings_source, str)


def test_load_concurrent(concurrent_sources, config_loader):
    loader = SourceLoader(SourceLoaderSettings(concurrent=True, n_threads=4), config_loader=config_loader)
    start_time = time.time()
    output = loader.load(concurrent_sources)
    duration = time.time() - start_time

    # Rough check that concurrency reduces total time (12 slow sources ~0.05s should take at least 0.55s if serial)
    assert duration < 0.3

    assert output.template_str == "template"
    assert output.schema_config == {"config": "schema"}
    assert [v["config"] for v in output.variants_configs] == ["variant0", "variant1", "variant2", "variant3"]       # type: ignore
    assert isinstance(output.template_engine_settings, Settings)
    assert isinstance(output.template_parser_settings, Settings)
    assert isinstance(output.schema_parser_settings_source, Settings)
    assert isinstance(output.variant_parser_settings_source, Settings)
    assert isinstance(output.compiler_settings_source, Settings)
    assert isinstance(output.renderer_settings_source, Settings)

    # Compare serial vs concurrent outputs
    serial_loader = SourceLoader(SourceLoaderSettings(concurrent=False), config_loader=config_loader)
    start_time = time.time()
    serial_output = serial_loader.load(concurrent_sources)
    duration = time.time() - start_time
    assert duration > 0.5

    assert output.template_str == serial_output.template_str
    assert output.schema_config == serial_output.schema_config
    assert [v["config"] for v in output.variants_configs] == [v["config"] for v in serial_output.variants_configs]      # type: ignore
