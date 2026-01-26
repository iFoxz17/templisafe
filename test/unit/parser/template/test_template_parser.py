import pytest
from templisafe.settings.template_parser_settings import TemplateParserSettings
from templisafe.parser.template.template_parser import TemplateParser
from templisafe.template.template_model import Template

def test_template_parser_returns_template():
    # Create dummy settings
    settings = TemplateParserSettings()
    
    # Instantiate the parser
    parser = TemplateParser(settings)
    
    # Sample template string and variables
    template_str = "SELECT * FROM users WHERE id = :user_id"
    vars_set = {"user_id"}
    
    # Parse
    result = parser.parse(template_str, vars_set)
    
    # Assertions
    assert isinstance(result, Template)
    assert result.template_str == template_str
    assert result.vars == vars_set
