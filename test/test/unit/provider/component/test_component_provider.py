from unittest.mock import Mock

import pytest

from templisafe.provider.component.component_provider import ComponentProvider

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def providers():
    return {
        "template_engine": Mock(),
        "template_parser": Mock(),
        "schema_parser": Mock(),
        "variant_parser": Mock(),
        "compiler": Mock(),
        "renderer": Mock(),
    }


@pytest.fixture
def component_provider(providers) -> ComponentProvider:
    return ComponentProvider(
        template_engine_provider=providers["template_engine"],
        template_parser_provider=providers["template_parser"],
        schema_parser_provider=providers["schema_parser"],
        variant_parser_provider=providers["variant_parser"],
        compiler_provider=providers["compiler"],
        renderer_provider=providers["renderer"],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_provide_template_engine_delegates(component_provider, providers):
    obj = object()
    providers["template_engine"].provide.return_value = obj

    result = component_provider.provide_template_engine()

    providers["template_engine"].provide.assert_called_once_with(None)
    assert result is obj


def test_provide_template_parser_delegates(component_provider, providers):
    obj = object()
    providers["template_parser"].provide.return_value = obj

    result = component_provider.provide_template_parser()

    providers["template_parser"].provide.assert_called_once()
    assert result is obj


def test_provide_schema_parser_delegates(component_provider, providers):
    obj = object()
    providers["schema_parser"].provide.return_value = obj

    result = component_provider.provide_schema_parser()

    providers["schema_parser"].provide.assert_called_once()
    assert result is obj


def test_provide_variant_parser_delegates(component_provider, providers):
    obj = object()
    providers["variant_parser"].provide.return_value = obj

    result = component_provider.provide_variant_parser()

    providers["variant_parser"].provide.assert_called_once()
    assert result is obj


def test_provide_compiler_delegates(component_provider, providers):
    obj = object()
    providers["compiler"].provide.return_value = obj

    result = component_provider.provide_compiler()

    providers["compiler"].provide.assert_called_once()
    assert result is obj


def test_provide_renderer_delegates(component_provider, providers):
    obj = object()
    providers["renderer"].provide.return_value = obj

    result = component_provider.provide_renderer()

    providers["renderer"].provide.assert_called_once()
    assert result is obj
