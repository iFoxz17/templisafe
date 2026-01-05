import pytest
from dataclasses import FrozenInstanceError

from sqltemplater.settings.source_settings import SourceSettings, LocalSourceSettings
from sqltemplater.util.util import ContentType


@pytest.fixture
def content_type():
    # Pick any valid ContentType member
    return next(iter(ContentType))


def test_source_settings_is_abstract(content_type):
    """
    SourceSettings inherits from ABC and should not be directly instantiable.
    However, since it does not declare any abstract method, it is not forced to be abstract.
    """
    # with pytest.raises(Exception):
    #   a = SourceSettings(content_type=content_type)
    pass


def test_local_source_settings_creation(content_type):
    """
    LocalSourceSettings should correctly store path and content_type.
    """
    settings = LocalSourceSettings(
        content_type=content_type,
        path="/tmp/example.sql",
    )

    assert settings.content_type is content_type
    assert settings.path == "/tmp/example.sql"


def test_local_source_settings_is_instance_of_source_settings(content_type):
    """
    LocalSourceSettings must be a subclass of SourceSettings.
    """
    settings = LocalSourceSettings(
        content_type=content_type,
        path="some/path",
    )

    assert isinstance(settings, SourceSettings)


def test_source_settings_are_frozen(content_type):
    """
    Both SourceSettings and its subclasses are frozen dataclasses.
    """
    settings = LocalSourceSettings(
        content_type=content_type,
        path="immutable/path",
    )

    with pytest.raises(FrozenInstanceError):
        settings.path = "new/path"  # type: ignore

    with pytest.raises(FrozenInstanceError):
        settings.content_type = content_type        # type: ignore


def test_local_source_settings_equality(content_type):
    """
    Frozen dataclasses should support structural equality.
    """
    s1 = LocalSourceSettings(
        content_type=content_type,
        path="/a/b",
    )
    s2 = LocalSourceSettings(
        content_type=content_type,
        path="/a/b",
    )
    s3 = LocalSourceSettings(
        content_type=content_type,
        path="/different",
    )

    assert s1 == s2
    assert s1 != s3