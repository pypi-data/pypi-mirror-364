from pathlib import Path

from pytest_fixture_collect import collect_fixture_file_paths


def test_collect_fixture_file_paths(tmp_path: Path) -> None:
    """
    Test folder structure:
    
        tests/
        └── fixtures/
            ├── __init__.py
            ├── f1.py
            └── sub_fixtures/
                ├── __init__.py
                └── f2.py

    """

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    fixtures_dir = tests_dir / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    init_file_1 = fixtures_dir / "__init__.py"
    init_file_1.write_text("")

    fixture_file_1 = fixtures_dir / "f1.py"
    fixture_file_1.write_text("")

    sub_fixtures_dir = fixtures_dir / "sub_fixtures"
    sub_fixtures_dir.mkdir(parents=True, exist_ok=True)

    init_file_2 = sub_fixtures_dir / "__init__.py"
    init_file_2.write_text("")
                           
    fixture_file_2 = sub_fixtures_dir / "f2.py"
    fixture_file_2.write_text("")

    paths = collect_fixture_file_paths(root_dir=tmp_path, fixtures_dir=fixtures_dir)
    assert paths == ["tests.fixtures.f1", "tests.fixtures.sub_fixtures.f2"]
