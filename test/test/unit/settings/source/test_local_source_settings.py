from templisafe.settings.source.local_source_settings import LocalSourceSettings
from templisafe.settings.source.source_settings import SourceKind, SourceSettings

# -----------------------------
# Fixtures / example configs
# -----------------------------
LOCAL_CONFIG_DICT = {"kind": "local", "path": "/tmp/query.sql"}


LOCAL_YAML = """
kind: local
path: "/tmp/query.sql"
"""

LOCAL_JSON = '{"kind": "local", "path": "/tmp/query.sql"}'


# -----------------------------
# Tests for create()
# -----------------------------
def test_create_local_from_dict():
    instance = SourceSettings.create(**LOCAL_CONFIG_DICT)
    assert isinstance(instance, LocalSourceSettings)
    assert instance.kind == SourceKind.LOCAL
    assert instance.path == "/tmp/query.sql"


# -----------------------------
# Tests for from_dict()
# -----------------------------
def test_from_dict_local():
    instance = LocalSourceSettings.from_dict(LOCAL_CONFIG_DICT)
    assert isinstance(instance, LocalSourceSettings)
    assert instance.path == "/tmp/query.sql"


# -----------------------------
# Tests for from_yaml()
# -----------------------------
def test_from_yaml_local():
    instance = LocalSourceSettings.from_yaml(LOCAL_YAML)
    assert isinstance(instance, LocalSourceSettings)
    assert instance.path == "/tmp/query.sql"


# -----------------------------
# Tests for from_json()
# -----------------------------
def test_from_json_local():
    instance = LocalSourceSettings.from_json(LOCAL_JSON)
    assert isinstance(instance, LocalSourceSettings)
    assert instance.path == "/tmp/query.sql"
