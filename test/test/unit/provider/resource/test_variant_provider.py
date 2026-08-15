from unittest.mock import Mock

import pytest

from templisafe.parser.config.config_parser import Config
from templisafe.parser.variant.variant_parser import VariantParser, VariantSet
from templisafe.provider.resource.variant_provider import VariantProvider
from templisafe.template.template_model import Binding, Variant


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def provider() -> VariantProvider:
    """Return a VariantProvider instance."""
    return VariantProvider()


@pytest.fixture
def config() -> Config:
    """Return a basic Config instance."""
    return {"variant_a": {"var": 1}, "variant_b": {"var": 2}}


@pytest.fixture
def parser() -> VariantParser:
    """Return a mocked VariantParser."""
    parser_mock = Mock(spec=VariantParser)
    variant_a: Variant = Variant("variant_a", [Binding(0, "var", 1)])
    variant_b: Variant = Variant("variant_b", [Binding(0, "var", 2)])
    parser_mock.parse.return_value = VariantSet([variant_a, variant_b])
    return parser_mock


# -----------------------------
# Tests
# -----------------------------
def test_provide_returns_variant_set(provider: VariantProvider, config: Config, parser: Mock):
    """Provider delegates parsing to the VariantParser and returns a VariantSet."""
    result = provider.provide(config, parser)

    # Verify return type and content
    assert isinstance(result, VariantSet)
    assert result == parser.parse.return_value

    # Verify parser was called with the config
    parser.parse.assert_called_once_with(config)
