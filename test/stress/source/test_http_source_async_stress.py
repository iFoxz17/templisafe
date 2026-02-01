import pytest
import pytest_asyncio
import asyncio
import requests
from aresponses import ResponsesMockServer
from time import perf_counter

from templisafe.source.http.http_source import HttpSource
from templisafe.settings.source.http.http_source_settings import HttpSourceSettings
from templisafe.exceptions.source_error import HttpSourceError
from templisafe.content.content import ContentType


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def json_url():
    """Standard JSON API URL for tests."""
    return "https://api.example.com/data"


@pytest.fixture
def html_url():
    """Standard HTML page URL for tests."""
    return "https://example.com/page"


# ============================================================================
# UTILITIES
# ============================================================================

async def read_with_context(source: HttpSource) -> str:
    async with source as s:
        return await s.aread()


# ============================================================================
# CONCURRENCY TESTS
# ============================================================================

@pytest.mark.asyncio
class TestHttpSourceConcurrency:
    """Test suite for concurrent execution and scalability of HttpSource."""

    async def test_concurrent_requests_respect_latency(self, aresponses):
        """Multiple concurrent aread() calls execute in parallel, not sequentially."""
        url = "https://api.example.com/slow"
        num_requests = 3
        latency = 0.5  # seconds

        async def slow_response(request):
            await asyncio.sleep(latency)
            return aresponses.Response(text="slow content", status=200)

        aresponses.add(
            "api.example.com",
            "/slow",
            "GET",
            slow_response,
            repeat=num_requests,
        )

        settings = HttpSourceSettings(url=url, content_type=ContentType.JSON)
        sources = [HttpSource(settings) for _ in range(num_requests)]

        start = perf_counter()
        # Use async context manager to open all sources
        results = await asyncio.gather(*(read_with_context(s) for s in sources))
        duration = perf_counter() - start

        assert all(r == "slow content" for r in results)

        max_time = latency * 1.5  # Allow 50% overhead
        min_time = latency * 0.9
        assert duration < max_time, f"Expected concurrent execution (~{latency}s), took {duration:.2f}s"
        assert duration >= min_time, f"Suspiciously fast: {duration:.2f}s (mock delay not working?)"

    async def test_scales_to_thousands_of_sources(self, aresponses):
        """HttpSource handles thousands of concurrent requests efficiently."""
        num_sources = 100
        base_url = "https://api.example.com"
        latency = 0.01  # 10ms simulated network latency

        async def fast_response(request):
            await asyncio.sleep(latency)
            path = request.path_qs
            return aresponses.Response(text=f"data-{path}", status=200)

        aresponses.add(
            "api.example.com",
            aresponses.ANY,
            "GET",
            fast_response,
            repeat=num_sources,
        )

        sources = [
            HttpSource(HttpSourceSettings(url=f"{base_url}/item/{i}", content_type=ContentType.JSON))
            for i in range(num_sources)
        ]

        start = perf_counter()
        results = await asyncio.gather(*(read_with_context(s) for s in sources))
        duration = perf_counter() - start

        assert len(results) == num_sources
        unique_results = set(results)
        assert len(unique_results) == num_sources

        sequential_time = num_sources * latency
        max_concurrent_time = sequential_time * 0.2  # Allow 20% of sequential time
        assert duration < max_concurrent_time, (
            f"Scaling issue: {num_sources} requests took {duration:.2f}s. "
            f"Expected < {max_concurrent_time:.2f}s for concurrent execution. "
            f"Sequential would take {sequential_time:.2f}s."
        )

        print(
            f"\n✅ {num_sources} concurrent requests in {duration:.2f}s "
            f"({duration/num_sources*1000:.2f}ms avg, "
            f"{sequential_time/duration:.1f}x speedup)"
        )

    async def test_memory_efficiency_with_many_sources(self, aresponses):
        """Creating many HttpSource instances doesn't consume excessive memory."""
        import tracemalloc

        num_sources = 5000
        max_memory_mb = 50

        async def mock_response(request):
            return aresponses.Response(text="test", status=200)

        aresponses.add(
            "api.example.com",
            aresponses.ANY,
            "GET",
            mock_response,
            repeat=num_sources,
        )

        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        sources = [
            HttpSource(HttpSourceSettings(url=f"https://api.example.com/item/{i}", content_type=ContentType.JSON))
            for i in range(num_sources)
        ]

        results = await asyncio.gather(*(read_with_context(s) for s in sources))

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        total_memory_mb = sum(stat.size_diff for stat in stats) / (1024 * 1024)

        assert len(results) == num_sources
        assert total_memory_mb < max_memory_mb, (
            f"Memory usage too high: {total_memory_mb:.2f}MB for {num_sources} sources. "
            f"Expected < {max_memory_mb}MB (shared session should be efficient)"
        )

        print(
            f"\n✅ Memory efficiency: {total_memory_mb:.2f}MB for {num_sources} sources "
            f"({total_memory_mb/num_sources*1024:.2f}KB per source)"
        )

    async def test_concurrent_requests_to_multiple_hosts(self, aresponses):
        """Concurrent requests work correctly across multiple different hosts."""
        num_per_host = 500
        hosts = ["api1.example.com", "api2.example.com", "api3.example.com"]
        latency = 0.01

        async def mock_response(request):
            await asyncio.sleep(latency)
            return aresponses.Response(text=f"response-{request.host}", status=200)

        for host in hosts:
            aresponses.add(host, aresponses.ANY, "GET", mock_response, repeat=num_per_host)

        sources = [
            HttpSource(HttpSourceSettings(url=f"https://{host}/item/{i}", content_type=ContentType.JSON))
            for host in hosts
            for i in range(num_per_host)
        ]

        start = perf_counter()
        results = await asyncio.gather(*(read_with_context(s) for s in sources))        
        duration = perf_counter() - start

        total_sources = len(hosts) * num_per_host
        assert len(results) == total_sources

        for host in hosts:
            host_responses = [r for r in results if host in r]
            assert len(host_responses) == num_per_host

        max_time = 2.0
        assert duration < max_time, f"Multi-host concurrent execution took too long: {duration:.2f}s"

        print(f"\n✅ {total_sources} requests across {len(hosts)} hosts in {duration:.2f}s")
