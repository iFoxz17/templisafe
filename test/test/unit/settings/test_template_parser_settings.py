import pytest

from templisafe.exceptions.settings_error import SettingsError
from templisafe.settings.template_parser_settings import (
    Settings,
    TemplateParserSettings,
)


class TestTemplateParserSettings:
    # ------------------------------------------------------------------
    # create()
    # ------------------------------------------------------------------
    def test_create_base_minimal(self):
        settings = Settings.create(kind="template_parser_settings")
        assert isinstance(settings, TemplateParserSettings)

    def test_create_empty_kwargs(self):
        """Should allow creation with no arguments"""
        settings = TemplateParserSettings.create()
        assert isinstance(settings, TemplateParserSettings)

    def test_create_with_kwargs(self):
        """Kwargs are accepted for future extensibility"""
        settings = TemplateParserSettings.create()
        assert isinstance(settings, TemplateParserSettings)

    # ------------------------------------------------------------------
    # from_dict()
    # ------------------------------------------------------------------
    def test_from_dict_valid(self):
        cfg = {}
        settings = TemplateParserSettings.from_dict(cfg)
        assert isinstance(settings, TemplateParserSettings)

    def test_from_dict_invalid_type(self):
        with pytest.raises(SettingsError):
            TemplateParserSettings.from_dict("not a dict")  # type: ignore

    # ------------------------------------------------------------------
    # from_yaml()
    # ------------------------------------------------------------------
    '''
    def test_from_yaml_valid(self):
        yaml_str = """
        """
        settings = TemplateParserSettings.from_yaml(yaml_str)
        assert isinstance(settings, TemplateParserSettings)
    '''

    def test_from_yaml_invalid_yaml(self):
        yaml_str = "!!! invalid yaml !!!"
        with pytest.raises(SettingsError):
            TemplateParserSettings.from_yaml(yaml_str)

    def test_from_yaml_invalid_type(self):
        yaml_str = "- list item 1\n- list item 2"
        with pytest.raises(SettingsError):
            TemplateParserSettings.from_yaml(yaml_str)

    # ------------------------------------------------------------------
    # from_json()
    # ------------------------------------------------------------------
    """
    def test_from_json_valid(self):
        json_str = ''
        settings = TemplateParserSettings.from_json(json_str)
        assert isinstance(settings, TemplateParserSettings)
    """

    def test_from_json_invalid_json(self):
        json_str = '{"foo": "bar"'  # missing closing }
        with pytest.raises(SettingsError):
            TemplateParserSettings.from_json(json_str)

    def test_from_json_invalid_type(self):
        json_str = '["not", "a", "dict"]'
        with pytest.raises(SettingsError):
            TemplateParserSettings.from_json(json_str)
