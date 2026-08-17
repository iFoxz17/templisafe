# Tests

Pytest configuration lives in `test/pytest.ini`. The executable test suites live
under `test/test/`.

Run the full suite from the repository root:

```bash
python -m pytest -c test/pytest.ini
```

Useful subsets:

```bash
python -m pytest -c test/pytest.ini -m unit
python -m pytest -c test/pytest.ini -m integration
python -m pytest -c test/pytest.ini -m stress
python -m pytest -c test/pytest.ini -m "source and http"
```

Run CI quality checks locally:

```bash
python -m ruff check src test
python -m ruff format --check src test
python -m mypy src
```

Run a file or a single test:

```bash
python -m pytest -c test/pytest.ini test/test/integration/test_templater_public_api.py
python -m pytest -c test/pytest.ini test/test/integration/test_templater_public_api.py::test_compile_render_validate_and_build_with_inline_sources
```

Add tests under the matching suite folder and rely on the central marker hook in
`test/test/conftest.py` to apply suite and package markers automatically.
