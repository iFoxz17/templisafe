from pydantic import BaseModel
import pytest
from unittest.mock import create_autospec
import asyncio
import time

from templisafe.settings.settings import Settings
from templisafe.loader.loader_facade import LoaderFacade
from templisafe.loader.config.config_loader import ConfigLoader
from templisafe.loader.template.template_loader import TemplateLoader
from templisafe.loader.schema.schema_loader import SchemaLoader
from templisafe.loader.variant.variant_loader import VariantLoader
from templisafe.source.source import Source
from templisafe.template.template_model import Template, Schema, VariantSet

# -------------------------
# Dummy Settings subclass
# -------------------------
class DummySettings(Settings):
    foo: str
    bar: int

    @classmethod
    def _parse_config(cls, config: dict, **kwargs) -> "DummySettings":
        return cls.model_validate(config)

class SlowSource(Source):
    """Custom Source that sleeps before returning dummy content."""
    def __init__(self, name: str, delay: float = 0.5):
        self.name = name
        self.delay = delay

    def read(self) -> str:
        time.sleep(self.delay)
        return f"vars:\n\t{self.name}: {self.delay}"
    
class FailingSource(Source):
    """Custom Source that raises an exception when read."""
    def __init__(self, name: str):
        self.name = name

    def read(self):
        raise RuntimeError(f"Failed to read source {self.name}")


# -------------------------
# Fixtures for the loaders
# -------------------------
@pytest.fixture
def config_loader():
    return create_autospec(ConfigLoader)

@pytest.fixture
def template_loader():
    return create_autospec(TemplateLoader)

@pytest.fixture
def schema_loader():
    return create_autospec(SchemaLoader)

@pytest.fixture
def variant_loader():
    return create_autospec(VariantLoader)

@pytest.fixture
def facade(config_loader, template_loader, schema_loader, variant_loader) -> LoaderFacade:
    return LoaderFacade(
        config_loader=config_loader,
        template_loader=template_loader,
        schema_loader=schema_loader,
        variant_loader=variant_loader
    )

@pytest.fixture
def source():
    return create_autospec(Source)

# -------------------------
# Tests
# -------------------------
def test_load_settings_calls_config_loader(facade: LoaderFacade, config_loader, source):
    # Prepare dummy Settings
    mock_settings = DummySettings.model_validate({"foo": "bar", "bar": 42})
    config_loader.load_settings.return_value = mock_settings

    result = facade.load_settings(source)
    
    config_loader.load_settings.assert_called_once_with(source)
    assert result == mock_settings

def test_load_template_calls_template_loader(facade: LoaderFacade, template_loader, source):
    mock_template = Template(template_str="{{ x }}", vars={"x"})
    template_loader.load.return_value = mock_template

    result = facade.load_template(source)

    template_loader.load.assert_called_once_with(source, None)
    assert result == mock_template

def test_load_schema_calls_schema_loader_and_config_loader(facade: LoaderFacade, schema_loader, config_loader, source):
    mock_schema = Schema(model_cls=BaseModel)
    schema_loader.load.return_value = mock_schema
    config_loader.load_config.return_value = {"parameters": {}}

    result = facade.load_schema(source)

    config_loader.load_config.assert_called_once_with(source)
    schema_loader.load.assert_called_once_with({"parameters": {}}, None)
    assert result == mock_schema

@pytest.mark.asyncio
async def test_load_variants_calls_variant_loader_and_config_loader(facade: LoaderFacade, variant_loader, config_loader):
    mock_variant_set = VariantSet([])
    variant_loader.load.return_value = mock_variant_set

    source1 = create_autospec(Source)
    source2 = create_autospec(Source)
    config_loader.load_config.side_effect = [{"vars": {}}, {"vars": {}}]

    result = await facade.load_variants([source1, source2])

    assert config_loader.load_config.call_count == 2
    variant_loader.load.assert_called_once_with([{"vars": {}}, {"vars": {}}], None)
    assert result == mock_variant_set


@pytest.mark.asyncio
async def test_load_variants_concurrent():
    config_loader = create_autospec(ConfigLoader)
    variant_loader = create_autospec(VariantLoader)

    # VariantLoader just returns an empty VariantSet
    variant_loader.load.return_value = VariantSet([])

    facade = LoaderFacade(
        config_loader=config_loader,
        template_loader=create_autospec(None),
        schema_loader=create_autospec(None),
        variant_loader=variant_loader
    )

    # Create two slow sources
    slow1 = SlowSource("s1", delay=0.5)
    slow2 = SlowSource("s2", delay=0.5)
    slow3 = SlowSource("s3", delay=0.5)
    slow4 = SlowSource("s4", delay=0.5)

    # Patch config_loader.load_config to call source.read()
    config_loader.load_config.side_effect = lambda source: source.read()

    start_time = time.perf_counter()
    await facade.load_variants([slow1, slow2, slow3, slow4])
    elapsed = time.perf_counter() - start_time

    # Each source sleeps 0.5s; if sequential it would be ~2s
    # If concurrent, it should be ~0.5s (+small overhead)
    assert elapsed < 1, f"Method is not concurrent, elapsed={elapsed:.2f}s"

    # Ensure config_loader.load_config called for both sources
    assert config_loader.load_config.call_count == 4
    variant_loader.load.assert_called_once()


@pytest.mark.asyncio
async def test_load_variants_source_raises():
    config_loader = create_autospec(ConfigLoader)
    variant_loader = create_autospec(VariantLoader)
    variant_loader.load.return_value = VariantSet([])

    facade = LoaderFacade(
        config_loader=config_loader,
        template_loader=create_autospec(None),
        schema_loader=create_autospec(None),
        variant_loader=variant_loader
    )

    good_source = create_autospec(Source)
    good_source.read.return_value = {"vars": {"x": 1}}

    failing_source = FailingSource("bad_source")

    # Patch config_loader.load_config to call source.read()
    def side_effect(source):
        return source.read()
    config_loader.load_config.side_effect = side_effect

    # Expect the RuntimeError to propagate
    with pytest.raises(Exception):
        await facade.load_variants([good_source, failing_source])

    # Verify that config_loader.load_config was called for both sources
    assert config_loader.load_config.call_count == 2
    # Variant loader should not have been called due to error
    variant_loader.load.assert_not_called()


def test_load_schema_with_wrong_settings_type_raises(facade: LoaderFacade, config_loader, source):
    # Provide a parser settings that is NOT SchemaParserSettings
    config_loader.load_settings.return_value = DummySettings.model_validate({"foo": "bar", "bar": 42})
    config_loader.load_config.return_value = {"parameters": {}}

    with pytest.raises(ValueError):
        facade.load_schema(source, parser_settings_source=source)

@pytest.mark.asyncio
async def test_load_variants_with_wrong_settings_type_raises(facade: LoaderFacade, config_loader):
    # Provide a parser settings that is NOT VariantParserSettings
    config_loader.load_settings.return_value = DummySettings.model_validate({"foo": "bar", "bar": 42})
    source1 = create_autospec(Source)
    source2 = create_autospec(Source)
    config_loader.load_config.side_effect = [{"vars": {}}, {"vars": {}}]

    with pytest.raises(ValueError):
        await facade.load_variants([source1, source2], parser_settings_source=source1)
