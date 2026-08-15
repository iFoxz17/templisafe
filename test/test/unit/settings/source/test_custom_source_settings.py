import json

import pytest

from templisafe.exceptions.settings_error import SettingsError
from templisafe.settings.source.custom_source_settings import CustomSourceSettings
from templisafe.settings.source.source_settings import SourceKind, SourceSettings

CONTEXT: dict = {"x": "y", "f": 2.3, "z": [1, 2, 3], "record": {"a": "b"}}

# -----------------------------
# Fixtures / example configs
# -----------------------------
CUSTOM_CONFIG_DICT = {"kind": "custom", "context": CONTEXT}

CUSTOM_YAML = """
kind: custom
context:
    x: y
    f: 2.3
    z: [1, 2, 3]
    record:
        a: b
"""

CUSTOM_JSON = f"""
    {{
        "kind": "custom", 
        "context": {json.dumps(CONTEXT)}
    }}
"""


# -----------------------------
# Test for create()
# -----------------------------
def test_create_custom_from_dict():
    instance = SourceSettings.create(**CUSTOM_CONFIG_DICT)
    assert isinstance(instance, CustomSourceSettings)
    assert instance.kind == SourceKind.CUSTOM
    assert instance.context == CONTEXT


# -----------------------------
# Test for from_dict()
# -----------------------------
def test_from_dict_custom():
    instance = CustomSourceSettings.from_dict(CUSTOM_CONFIG_DICT)
    assert isinstance(instance, CustomSourceSettings)
    assert instance.context == CONTEXT


# -----------------------------
# Test for from_yaml()
# -----------------------------
def test_from_yaml_custom():
    instance = CustomSourceSettings.from_yaml(CUSTOM_YAML)
    assert isinstance(instance, CustomSourceSettings)
    assert instance.context == CONTEXT


# -----------------------------
# Test for from_json()
# -----------------------------
def test_from_json_custom():
    instance = CustomSourceSettings.from_json(CUSTOM_JSON)
    assert isinstance(instance, CustomSourceSettings)
    assert instance.context == CONTEXT


# -----------------------------
# Test without context
# -----------------------------
def test_custom_no_context():
    instance = SourceSettings.create(kind="custom")
    assert isinstance(instance, CustomSourceSettings)
    assert instance.context is None
