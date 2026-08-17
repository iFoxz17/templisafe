import os
import subprocess
import sys
import textwrap
from pathlib import Path


def run_with_blocked_optional_dependencies(script: str) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[3]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(repo_root / "src"), env.get("PYTHONPATH", "")])

    blocker = """
import importlib.abc
import sys


class OptionalDependencyBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "boto3" or fullname.startswith("boto3."):
            raise ModuleNotFoundError(f"No module named {fullname!r}", name="boto3")
        if fullname == "botocore" or fullname.startswith("botocore."):
            raise ModuleNotFoundError(f"No module named {fullname!r}", name="botocore")
        if fullname == "aiohttp" or fullname.startswith("aiohttp."):
            raise ModuleNotFoundError(f"No module named {fullname!r}", name="aiohttp")
        if fullname == "django" or fullname.startswith("django."):
            raise ModuleNotFoundError(f"No module named {fullname!r}", name="django")
        return None


sys.meta_path.insert(0, OptionalDependencyBlocker())
"""

    return subprocess.run(
        [sys.executable, "-c", blocker + "\n" + textwrap.dedent(script)],
        capture_output=True,
        env=env,
        text=True,
        check=False,
    )


def test_package_import_and_inline_workflow_do_not_require_optional_dependencies() -> None:
    result = run_with_blocked_optional_dependencies(
        """
        from templisafe import ContentType, SourceSettings, TemplaterFactory

        template = SourceSettings.create(
            kind="inline",
            content="Hello {{ name }}!",
            content_type=ContentType.TEXT,
        )
        schema = SourceSettings.create(
            kind="inline",
            content="schema:\\n  name: str\\n",
            content_type=ContentType.YAML,
        )
        variants = SourceSettings.create(
            kind="inline",
            content="variants:\\n  name: default\\n  bindings:\\n    name: World\\n",
            content_type=ContentType.YAML,
        )

        build = TemplaterFactory().create(diagnostic_policy="ignore").build(
            template=template,
            schema=schema,
            variants=variants,
        )

        assert build.rendering.rendered["default"].rendered_str == "Hello World!"
        """
    )

    assert result.returncode == 0, result.stderr


def test_aws_source_read_reports_missing_optional_dependency() -> None:
    result = run_with_blocked_optional_dependencies(
        """
        from templisafe.content.content import ContentType
        from templisafe.exceptions.source_error import MissingOptionalSourceDependencyError
        from templisafe.settings.source.aws.aws_s3_bucket_source_settings import AwsS3BucketSourceSettings
        from templisafe.source import AwsS3BucketSource

        source = AwsS3BucketSource(
            AwsS3BucketSourceSettings(
                bucket="bucket",
                key="key",
                content_type=ContentType.TEXT,
            )
        )

        try:
            source.read()
        except MissingOptionalSourceDependencyError as exc:
            assert exc.dependency == "boto3"
            assert exc.extra == "s3"
        else:
            raise AssertionError("AWS source read should require the s3 extra when boto3 is missing")
        """
    )

    assert result.returncode == 0, result.stderr


def test_http_async_open_reports_missing_optional_dependency() -> None:
    result = run_with_blocked_optional_dependencies(
        """
        import asyncio

        from templisafe import ContentType
        from templisafe.exceptions.source_error import MissingOptionalSourceDependencyError
        from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
        from templisafe.source.http.http_source import HttpSource

        async def main():
            source = HttpSource(
                HttpSourceSettings(
                    url="https://example.com",
                    content_type=ContentType.TEXT,
                )
            )
            try:
                await source.aopen()
            except MissingOptionalSourceDependencyError as exc:
                assert exc.dependency == "aiohttp"
                assert exc.extra == "http-async"
            else:
                raise AssertionError("Async HTTP source should require the http-async extra when aiohttp is missing")

        asyncio.run(main())
        """
    )

    assert result.returncode == 0, result.stderr
