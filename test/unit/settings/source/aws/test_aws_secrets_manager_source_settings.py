import pytest
import json

from templisafe.settings.source.source_settings import SourceSettings, SourceKind
from templisafe.settings.source.aws.aws_secrets_manager_source_settings import AwsSecretsManagerSourceSettings
from templisafe.exceptions.settings_error import SettingsError

# -----------------------------
# Fixtures / example configs
# -----------------------------
SECRETS_MANAGER_CONFIG_DICT = {
    "kind": "aws_secrets_manager",
    "secret_id": "myapp/secret.json",
    "version_id": "EXAMPLE1-123",
    "version_stage": "AWSCURRENT",
    "aws_access_key_id": "AKIAFAKE",
    "aws_secret_access_key": "SECRETFAKE",
    "aws_session_token": "SESSIONFAKE",
    "region_name": "us-east-1",
    "endpoint_url": "http://localhost:4566"
}

SECRETS_MANAGER_YAML = """
kind: aws_secrets_manager
secret_id: myapp/secret.json
version_id: EXAMPLE1-123
version_stage: AWSCURRENT
aws_access_key_id: AKIAFAKE
aws_secret_access_key: SECRETFAKE
aws_session_token: SESSIONFAKE
region_name: us-east-1
endpoint_url: http://localhost:4566
"""

SECRETS_MANAGER_JSON = json.dumps(SECRETS_MANAGER_CONFIG_DICT)

# -----------------------------
# Tests for create()
# -----------------------------
def test_create_secrets_manager_only_required():
    instance = AwsSecretsManagerSourceSettings(secret_id="myapp/secret.json")
    assert isinstance(instance, AwsSecretsManagerSourceSettings)
    assert instance.kind == SourceKind.AWS_SECRETS_MANAGER
    assert instance.secret_id == "myapp/secret.json"
    # Optional fields should be None
    assert instance.version_id is None
    assert instance.version_stage is None
    assert instance.aws_access_key_id is None

def test_create_secrets_manager_from_dict():
    instance = SourceSettings.create(**SECRETS_MANAGER_CONFIG_DICT)
    assert isinstance(instance, AwsSecretsManagerSourceSettings)
    assert instance.kind == SourceKind.AWS_SECRETS_MANAGER
    assert instance.secret_id == "myapp/secret.json"
    assert instance.version_id == "EXAMPLE1-123"
    assert instance.version_stage == "AWSCURRENT"
    assert instance.aws_access_key_id == "AKIAFAKE"
    assert instance.aws_secret_access_key == "SECRETFAKE"
    assert instance.aws_session_token == "SESSIONFAKE"
    assert instance.region_name == "us-east-1"
    assert instance.endpoint_url == "http://localhost:4566"

def test_create_missing_required_field_raises():
    cfg = SECRETS_MANAGER_CONFIG_DICT.copy()
    cfg.pop("secret_id")
    with pytest.raises(ValueError, match="Invalid fields"):
        SourceSettings.create(**cfg)

def test_create_extra_field_raises():
    cfg = SECRETS_MANAGER_CONFIG_DICT.copy()
    cfg["extra"] = 123  # type: ignore
    with pytest.raises(ValueError):
        SourceSettings.create(**cfg)

# -----------------------------
# Tests for from_dict()
# -----------------------------
def test_from_dict_secrets_manager():
    instance = AwsSecretsManagerSourceSettings.from_dict(SECRETS_MANAGER_CONFIG_DICT)
    assert isinstance(instance, AwsSecretsManagerSourceSettings)
    assert instance.secret_id == "myapp/secret.json"
    assert instance.version_id == "EXAMPLE1-123"
    assert instance.version_stage == "AWSCURRENT"

# -----------------------------
# Tests for from_yaml()
# -----------------------------
def test_from_yaml_secrets_manager():
    instance = AwsSecretsManagerSourceSettings.from_yaml(SECRETS_MANAGER_YAML)
    assert isinstance(instance, AwsSecretsManagerSourceSettings)
    assert instance.secret_id == "myapp/secret.json"
    assert instance.version_id == "EXAMPLE1-123"
    assert instance.version_stage == "AWSCURRENT"

def test_from_yaml_invalid_yaml_raises():
    invalid_yaml = "this: [unbalanced"
    with pytest.raises(SettingsError):
        AwsSecretsManagerSourceSettings.from_yaml(invalid_yaml)

def test_from_yaml_not_a_dict_raises():
    yaml_list = "- item1\n- item2"
    with pytest.raises(SettingsError):
        AwsSecretsManagerSourceSettings.from_yaml(yaml_list)

# -----------------------------
# Tests for from_json()
# -----------------------------
def test_from_json_secrets_manager():
    instance = AwsSecretsManagerSourceSettings.from_json(SECRETS_MANAGER_JSON)
    assert isinstance(instance, AwsSecretsManagerSourceSettings)
    assert instance.secret_id == "myapp/secret.json"
    assert instance.version_id == "EXAMPLE1-123"
    assert instance.version_stage == "AWSCURRENT"

def test_from_json_invalid_json_raises():
    invalid_json = '{"foo": "bar",}'
    with pytest.raises(SettingsError):
        AwsSecretsManagerSourceSettings.from_json(invalid_json)

def test_from_json_not_a_dict_raises():
    json_list = '["a", "b"]'
    with pytest.raises(SettingsError):
        AwsSecretsManagerSourceSettings.from_json(json_list)
