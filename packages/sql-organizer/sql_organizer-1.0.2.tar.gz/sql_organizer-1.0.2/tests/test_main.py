from collections.abc import Sequence
from pathlib import Path

import pytest
from typer.testing import CliRunner

from sql_organizer.main import app


@pytest.fixture(scope="module")
def cli_runner() -> CliRunner:
    return CliRunner()


def _create_files(tmp_path: Path, files: Sequence[str]):
    for file in files:
        (tmp_path / file).mkdir(parents=True, exist_ok=True)


def test_search(cli_runner, tmp_path):
    files = ["test.sql", "folder/other.txt", "bad.py"]
    _create_files(tmp_path, files)
    result = cli_runner.invoke(
        app, [str(tmp_path.absolute()), "-e", "txt", "-e", "sql"]
    )
    output = result.output.replace("\n", "")
    assert result.exit_code == 0
    assert "test.sql" in output
    assert "other.txt" in output
    assert "bad.py" not in output


def test_search_invalid_sorter(cli_runner):
    result = cli_runner.invoke(app, ["-so", "a"])
    assert result.exit_code == 0
    assert result.output.strip() == "Value Error! sorter a is invalid"


def test_search_empty_extension(cli_runner):
    result = cli_runner.invoke(app, ["-e", ""])
    assert result.exit_code == 0
    assert (
        result.output.strip() == "Value Error! Extension should not be an empty string"
    )
