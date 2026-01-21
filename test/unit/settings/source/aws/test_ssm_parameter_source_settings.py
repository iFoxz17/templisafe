import pytest
import json

from templisafe.settings.source.source_settings import (
    SourceSettings,
    SourceKind,
)
from templisafe.settings.source.aws.aws_ssm_parameter_source_settings import (
    AwsSsmParameterSourceSettings,
)
from templisafe.exceptions.settings_error import SettingsError


# -----------------------------
# Fixtures / example configs
# -----------------------------
SSM_CONFIG_DICT = {
    "kind": "aws_ssm_parameter",
    "parameter_name": "/my/app/parameter",
    "with_decryption": True,
    "aws_access_key_id": "AKIAFAKE",
    "aws_secret_access_key": "SECRETFAKE",
    "region_name": "us-east-1",
    "endpoint_url": "http://localhost:4566",
}

SSM_YAML = """
kind: aws_ssm_parameter
parameter_name: /my/app/parameter
with_decryption: true
aws_access_key_id: AKIAFAKE
aws_secret_access_key: SECRETFAKE
region_name: us-east-1
endpoint_url: http://localhost:4566
"""

SSM_JSON = json.dumps(SSM_CONFIG_DICT)


# -----------------------------
# Tests for create()
# -----------------------------
def test_create_ssm_only_required():
    instance = AwsSsmParameterSourceSettings(
        parameter_name="/my/app/parameter",
    )

    assert isinstance(instance, AwsSsmParameterSourceSettings)
    assert instance.kind == SourceKind.AWS_SSM_PARAMETER
    assert instance.parameter_name == "/my/app/parameter"
    assert instance.with_decryption is True


def test_create_ssm_from_dict():
    instance = SourceSettings.create(**SSM_CONFIG_DICT)

    assert isinstance(instance, AwsSsmParameterSourceSettings)
    assert instance.kind == SourceKind.AWS_SSM_PARAMETER
    assert instance.parameter_name == "/my/app/parameter"
    assert instance.with_decryption is True
    assert instance.aws_access_key_id == "AKIAFAKE"
    assert instance.aws_secret_access_key == "SECRETFAKE"
    assert instance.region_name == "us-east-1"
    assert instance.endpoint_url == "http://localhost:4566"


def test_create_missing_required_field_raises():
    cfg = SSM_CONFIG_DICT.copy()
    cfg.pop("parameter_name")

    with pytest.raises(ValueError, match="Invalid fields"):
        SourceSettings.create(**cfg)


def test_create_extra_field_raises():
    cfg = SSM_CONFIG_DICT.copy()
    cfg["extra"] = 123  # type: ignore

    with pytest.raises(ValueError):
        SourceSettings.create(**cfg)


# -----------------------------
# Tests for from_dict()
# -----------------------------
def test_from_dict_ssm():
    instance = AwsSsmParameterSourceSettings.from_dict(SSM_CONFIG_DICT)

    assert isinstance(instance, AwsSsmParameterSourceSettings)
    assert instance.parameter_name == "/my/app/parameter"
    assert instance.with_decryption is True


# -----------------------------
# Tests for from_yaml()
# -----------------------------
def test_from_yaml_ssm():
    instance = AwsSsmParameterSourceSettings.from_yaml(SSM_YAML)

    assert isinstance(instance, AwsSsmParameterSourceSettings)
    assert instance.parameter_name == "/my/app/parameter"
    assert instance.with_decryption is True


def test_from_yaml_invalid_yaml_raises():
    invalid_yaml = "this: [unbalanced"

    with pytest.raises(SettingsError):
        AwsSsmParameterSourceSettings.from_yaml(invalid_yaml)


def test_from_yaml_not_a_dict_raises():
    yaml_list = "- item1\n- item2"

    with pytest.raises(SettingsError):
        AwsSsmParameterSourceSettings.from_yaml(yaml_list)


# -----------------------------
# Tests for from_json()
# -----------------------------
def test_from_json_ssm():
    instance = AwsSsmParameterSourceSettings.from_json(SSM_JSON)

    assert isinstance(instance, AwsSsmParameterSourceSettings)
    assert instance.parameter_name == "/my/app/parameter"
    assert instance.with_decryption is True


def test_from_json_invalid_json_raises():
    invalid_json = '{"foo": "bar",}'

    with pytest.raises(SettingsError):
        AwsSsmParameterSourceSettings.from_json(invalid_json)


def test_from_json_not_a_dict_raises():
    json_list = '["a", "b"]'

    with pytest.raises(SettingsError):
        AwsSsmParameterSourceSettings.from_json(json_list)
