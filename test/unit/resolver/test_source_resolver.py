import time
import pytest
from typing import Any

from templisafe.resolver.source_resolver import SourceResolver, SourceResolutionRequest, SourceResolverSettings
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
        source.read()
        return Settings()


# --- Fixtures ---
@pytest.fixture
def config_loader():
    return DummyConfigLoader()


@pytest.fixture
def dummy_sources():
    """Sources for serial resolve test."""
    return SourceResolutionRequest(
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
def slow_sources():
    """Sources for concurrent resolve test with slow sources."""
    return SourceResolutionRequest(
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


def test_resolve_serial(dummy_sources, config_loader):
    resolver = SourceResolver(SourceResolverSettings(concurrent=False), config_loader=config_loader)
    output = resolver.resolve(dummy_sources)

    assert output.template_str == "template"
    assert output.schema_config == {"config": "schema"}
    assert [v["config"] for v in output.variants_configs] == ["variant0", "variant1", "variant2"]       # type: ignore
    assert isinstance(output.template_engine_settings, Settings)
    assert isinstance(output.template_parser_settings, Settings)
    assert isinstance(output.schema_parser_settings, Settings)
    assert isinstance(output.variant_parser_settings, Settings)
    assert isinstance(output.compiler_settings, Settings)
    assert isinstance(output.renderer_settings, Settings)


def test_resolve_concurrent(slow_sources, config_loader):
    resolver = SourceResolver(SourceResolverSettings(concurrent=True, n_threads=4), config_loader=config_loader)
    start_time = time.time()
    output = resolver.resolve(slow_sources)
    duration = time.time() - start_time

    # Rough check that concurrency reduces total time (12 sources with a latency of 0.05s should take at least 0.6s if serial)
    assert duration < 0.3

    assert output.template_str == "template"
    assert output.schema_config == {"config": "schema"}
    assert [v["config"] for v in output.variants_configs] == ["variant0", "variant1", "variant2", "variant3"]       # type: ignore
    assert isinstance(output.template_engine_settings, Settings)
    assert isinstance(output.template_parser_settings, Settings)
    assert isinstance(output.schema_parser_settings, Settings)
    assert isinstance(output.variant_parser_settings, Settings)
    assert isinstance(output.compiler_settings, Settings)
    assert isinstance(output.renderer_settings, Settings)

    # Compare serial vs concurrent outputs
    serial_loader = SourceResolver(SourceResolverSettings(concurrent=False), config_loader=config_loader)
    start_time = time.time()
    serial_output = serial_loader.resolve(slow_sources)
    duration = time.time() - start_time
    assert duration >= 0.6

    assert output.template_str == serial_output.template_str
    assert output.schema_config == serial_output.schema_config
    assert [v["config"] for v in output.variants_configs] == [v["config"] for v in serial_output.variants_configs]      # type: ignore


def test_resolve_compilation_default_settings(config_loader):
    resolver = SourceResolver(SourceResolverSettings(concurrent=True, n_threads=4), config_loader=config_loader)
    compilation_input = SourceResolutionRequest(
        template_source=DummySource("template"),
        schema_source=DummySource("schema"),
    )
    
    output = resolver.resolve(compilation_input)

    assert output.template_str == "template"
    assert output.schema_config == {"config": "schema"}
    assert output.variants_configs is None
    assert output.template_engine_settings is None
    assert output.template_parser_settings is None
    assert output.schema_parser_settings is None
    assert output.variant_parser_settings is None
    assert output.compiler_settings is None
    assert output.renderer_settings is None
    
    # Compare serial vs concurrent outputs
    serial_loader = SourceResolver(SourceResolverSettings(concurrent=False), config_loader=config_loader)
    serial_output = serial_loader.resolve(compilation_input)

    assert output.template_str == serial_output.template_str
    assert output.schema_config == serial_output.schema_config
    assert output.variants_configs == serial_output.variants_configs
    assert output.template_engine_settings == serial_output.template_engine_settings
    assert output.schema_parser_settings == serial_output.schema_parser_settings
    assert output.variant_parser_settings == serial_output.variant_parser_settings
    assert output.template_parser_settings == serial_output.template_parser_settings
    assert output.compiler_settings == serial_output.compiler_settings
    assert output.renderer_settings == serial_output.renderer_settings


def test_load_compilation_custom_settings(config_loader):
    resolver = SourceResolver(SourceResolverSettings(concurrent=True, n_threads=4), config_loader=config_loader)
    compilation_input = SourceResolutionRequest(
        template_source=DummySource("template"),
        schema_source=DummySource("schema"),
        template_engine_settings_source=DummySource("engine_settings"),
        template_parser_settings_source=DummySource("parser_settings"),
        schema_parser_settings_source=DummySource("schema_parser"),
        compiler_settings_source=DummySource("compiler"),
    )
    
    output = resolver.resolve(compilation_input)

    assert output.template_str == "template"
    assert output.schema_config == {"config": "schema"}
    assert output.template_engine_settings
    assert isinstance(output.template_engine_settings, Settings)
    assert isinstance(output.template_parser_settings, Settings)
    assert isinstance(output.schema_parser_settings, Settings)
    assert output.variant_parser_settings is None
    assert isinstance(output.compiler_settings, Settings)
    assert output.renderer_settings is None
    
    # Compare serial vs concurrent outputs
    serial_loader = SourceResolver(SourceResolverSettings(concurrent=False), config_loader=config_loader)
    serial_output = serial_loader.resolve(compilation_input)

    assert output.template_str == serial_output.template_str
    assert output.schema_config == serial_output.schema_config
    assert output.variants_configs == serial_output.variants_configs
    assert output.template_engine_settings == serial_output.template_engine_settings
    assert output.schema_parser_settings == serial_output.schema_parser_settings
    assert output.template_parser_settings == serial_output.template_parser_settings
    assert output.variant_parser_settings == serial_output.variant_parser_settings
    assert output.compiler_settings == serial_output.compiler_settings
    assert output.renderer_settings == serial_output.renderer_settings


def test_load_rendering_default_settings(config_loader):
    resolver = SourceResolver(SourceResolverSettings(concurrent=True, n_threads=4), config_loader=config_loader)
    rendering_input = SourceResolutionRequest(
        variants_sources=[DummySource(f"variant{i}") for i in range(3)],
    )
    
    output = resolver.resolve(rendering_input)

    assert output.template_str is None
    assert output.schema_config is None
    assert [v["config"] for v in output.variants_configs] == ["variant0", "variant1", "variant2"]       # type: ignore
    assert output.template_engine_settings is None
    assert output.template_parser_settings is None
    assert output.schema_parser_settings is None
    assert output.variant_parser_settings is None
    assert output.compiler_settings is None
    assert output.renderer_settings is None
    
    # Compare serial vs concurrent outputs
    serial_loader = SourceResolver(SourceResolverSettings(concurrent=False), config_loader=config_loader)
    serial_output = serial_loader.resolve(rendering_input)

    assert output.template_str == serial_output.template_str
    assert output.schema_config == serial_output.schema_config
    assert output.variants_configs == serial_output.variants_configs
    assert output.template_engine_settings == serial_output.template_engine_settings
    assert output.schema_parser_settings == serial_output.schema_parser_settings
    assert output.template_parser_settings == serial_output.template_parser_settings
    assert output.variant_parser_settings == serial_output.variant_parser_settings
    assert output.compiler_settings == serial_output.compiler_settings
    assert output.renderer_settings == serial_output.renderer_settings


def test_load_rendering_custom_settings(config_loader):
    resolver = SourceResolver(SourceResolverSettings(concurrent=True, n_threads=4), config_loader=config_loader)
    rendering_input = SourceResolutionRequest(
        variants_sources=[DummySource(f"variant{i}") for i in range(3)],
        template_engine_settings_source=DummySource("engine_settings"),
        variant_parser_settings_source=DummySource("variant_parser"),
        renderer_settings_source=DummySource("renderer"),
    )
    
    output = resolver.resolve(rendering_input)

    assert output.template_str is None
    assert output.schema_config is None
    assert [v["config"] for v in output.variants_configs] == ["variant0", "variant1", "variant2"]       # type: ignore
    assert isinstance(output.template_engine_settings, Settings)
    assert output.schema_parser_settings is None
    assert output.template_parser_settings is None
    assert isinstance(output.variant_parser_settings, Settings)
    assert output.compiler_settings is None
    assert isinstance(output.renderer_settings, Settings)
    
    # Compare serial vs concurrent outputs
    serial_loader = SourceResolver(SourceResolverSettings(concurrent=False), config_loader=config_loader)
    serial_output = serial_loader.resolve(rendering_input)

    assert output.template_str == serial_output.template_str
    assert output.schema_config == serial_output.schema_config
    assert output.variants_configs == serial_output.variants_configs
    assert output.template_engine_settings == serial_output.template_engine_settings
    assert output.template_parser_settings == serial_output.template_parser_settings
    assert output.schema_parser_settings == serial_output.schema_parser_settings
    assert output.variant_parser_settings == serial_output.variant_parser_settings
    assert output.compiler_settings == serial_output.compiler_settings
    assert output.renderer_settings == serial_output.renderer_settings
