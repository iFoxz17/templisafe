from unittest.mock import Mock

import pytest

from templisafe.content.content import ContentType
from templisafe.provider.source_provider import SourceProvider
from templisafe.settings.source.aws.aws_s3_bucket_source_settings import (
    AwsS3BucketSourceSettings,
)
from templisafe.settings.source.aws.aws_secrets_manager_source_settings import (
    AwsSecretsManagerSourceSettings,
)
from templisafe.settings.source.aws.aws_ssm_parameter_source_settings import (
    AwsSsmParameterSourceSettings,
)
from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.settings.source.local_source_settings import LocalSourceSettings
from templisafe.source.content_type_resolver import ContentTypeResolver
from templisafe.source.inline_source import InlineSource
from templisafe.source.source import Source
from templisafe.source.source_resolver import SourceResolver


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def mock_source_resolver():
    resolver = Mock(spec=SourceResolver)
    source = Mock(spec=Source)
    resolver.resolve.side_effect = lambda s: s if isinstance(s, Source) else source
    return resolver


@pytest.fixture
def mock_content_type_resolver():
    resolver = Mock(spec=ContentTypeResolver)
    resolver.resolve.return_value = ContentType.TEXT
    return resolver


@pytest.fixture
def provider(mock_source_resolver, mock_content_type_resolver):
    return SourceProvider(mock_source_resolver, mock_content_type_resolver)


# -----------------------------
# Tests
# -----------------------------
def test_provide_source_as_is(provider: SourceProvider):
    """If input is already a Source, it is returned via the resolver."""
    src = InlineSource(InlineSourceSettings(content="Hello", content_type=ContentType.TEXT))
    result = provider.provide(src)
    assert isinstance(result, Source)


def test_provide_source_settings_with_type(provider: SourceProvider):
    """If SourceSettings has a content_type, it is resolved without calling ContentTypeResolver."""
    settings = InlineSourceSettings(content="Hello", content_type=ContentType.TEXT)
    result = provider.provide(settings)
    assert isinstance(result, Source)
    # ContentTypeResolver should not be called
    provider._content_type_resolver.resolve.assert_not_called()  # type: ignore


@pytest.mark.parametrize(
    "source_settings",
    [
        LocalSourceSettings(path="/file.j2"),
        AwsS3BucketSourceSettings(bucket="bucket", key="key.json"),
        AwsSecretsManagerSourceSettings(secret_id="id.yaml"),
        AwsSsmParameterSourceSettings(parameter_name="param.txt"),
    ],
    ids=[
        "local_j2",
        "aws_s3_bucket_json",
        "aws_secrets_manager_yaml",
        "aws_ssm_parameter_txt",
    ],
)
def test_provide_source_settings_without_type_param(provider: SourceProvider, source_settings):
    """
    Parametrized test: If SourceSettings has no content_type, the ContentTypeResolver is used.
    """
    result = provider.provide(source_settings)
    assert isinstance(result, Source)
    provider._content_type_resolver.resolve.assert_called_once_with(source_settings)  # type: ignore
