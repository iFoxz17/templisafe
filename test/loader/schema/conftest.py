'''
import pytest

from sqltemplater.util.util import ContentType
from sqltemplater.loader.schema.qschema_parser import QSchemaParser
from sqltemplater.loader.schema.qschema_parser_manager import QSchemaParserFactory, QSchemaParserManager

# -----------------------
# DummyParser fixture
# -----------------------
class DummyParser:
    """Simulates a SchemaParser with parse() behavior."""
    def __init__(self, settings=None):
        self._settings = settings
        self.parse_called_with = None

    def parse(self, data):
        self.parse_called_with = data
        return f"parsed:{data}"

@pytest.fixture
def dummy_parser():
    return DummyParser()

# -----------------------
# DummyManager fixture
# -----------------------
class DummyManager:
    """Simulates SchemaParserManager returning a fixed parser per ContentType."""
    def __init__(self, parsers=None):
        self._parsers = parsers or {}

    def get_or_create(self, type_):
        return self._parsers[type_]

@pytest.fixture
def dummy_manager(dummy_parser):
    return DummyManager(parsers={ContentType.YAML: dummy_parser})
    '''