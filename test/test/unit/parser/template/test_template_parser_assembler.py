from templisafe.parser.template.template_parser_assembler import TemplateParserAssembler
from templisafe.parser.template.template_parser_resolver import TemplateParserResolver
from templisafe.settings.manager_settings import ManagerSettings

CUSTOM_MANAGER_SETTINGS_YAML = """
cache: false
"""


def test_assemble_with_defaults():
    assembler = TemplateParserAssembler()

    resolver: TemplateParserResolver = assembler.assemble()

    assert isinstance(resolver, TemplateParserResolver)


def test_assemble_with_custom_manager_settings():
    assembler = TemplateParserAssembler()
    manager_settings = ManagerSettings.from_yaml(CUSTOM_MANAGER_SETTINGS_YAML)
    resolver = assembler.assemble(manager_settings=manager_settings)

    assert isinstance(resolver, TemplateParserResolver)
