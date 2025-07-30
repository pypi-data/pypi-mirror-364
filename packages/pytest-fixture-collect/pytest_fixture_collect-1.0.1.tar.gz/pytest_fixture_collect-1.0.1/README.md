# Pytest Fixture Collect

A utility to collect pytest fixture file paths.


```python
    # conftest.py
    from pathlib import Path

    from pytest_fixture_collect import collect_fixture_file_paths

    root_dir = ...  # absolute path of project root
    fixture_dir = ROOT_DIR / ...  # absolute path of fixture directory

    pytest_plugins = collect_fixture_file_paths(root_dir, fixture_dir)
```