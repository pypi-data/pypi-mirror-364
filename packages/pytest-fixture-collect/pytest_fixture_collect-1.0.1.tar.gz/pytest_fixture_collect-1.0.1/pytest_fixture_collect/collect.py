from pathlib import Path


def collect_fixture_file_paths(root_dir: Path, fixtures_dir: Path) -> list[str]:
    """
    Recursively collect all fixture file paths in a directory.
    Set the return value to a variable named `pytest_plugins` in
    a root `conftest.py` file of your project to inject the fixtures
    into your tests.

    ```python
        # conftest-py
        pytest_plugins = collect_fixture_file_paths(R00T_DIR, FIXTURES_DIR)
    ```
    """
    files = fixtures_dir.glob("**/*.py")
    return [
        _to_pytest_plugin_path(root_dir, f) for f in files if f.name != "__init__.py"
    ]
    

def _to_pytest_plugin_path(root_dir: Path, file_path: Path) -> str:
    dir_path = ".".join(file_path.relative_to(root_dir).parts[:-1])
    return f"{dir_path}.{file_path.stem}"
