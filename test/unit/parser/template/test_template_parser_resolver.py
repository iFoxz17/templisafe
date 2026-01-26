import pytest
from templisafe.parser.template.template_parser_resolver import TemplateParserResolver
from templisafe.parser.template.template_parser import TemplateParser
from templisafe.settings.template_parser_settings import TemplateParserSettings

CUSTOM_TEMPLATE_PARSER_SETTINGS_YAML = """
{}
"""

DEFAULT_TEMPLATE_PARSER_SETTINGS = TemplateParserSettings()  # Assuming default constructor works


def test_resolve_with_default_settings():
    resolver = TemplateParserResolver()
    parser = resolver.resolve(DEFAULT_TEMPLATE_PARSER_SETTINGS)

    assert isinstance(parser, TemplateParser)
    assert parser._settings == DEFAULT_TEMPLATE_PARSER_SETTINGS


def test_resolve_with_custom_settings():
    resolver = TemplateParserResolver()
    custom_settings = TemplateParserSettings.from_yaml(CUSTOM_TEMPLATE_PARSER_SETTINGS_YAML)
    parser = resolver.resolve(custom_settings)

    assert isinstance(parser, TemplateParser)
    assert parser._settings == custom_settings
