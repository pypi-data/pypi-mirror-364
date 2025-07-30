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
        new_file = tmp_path / file
        new_file.parent.mkdir(parents=True, exist_ok=True)
        with new_file.open("w") as f:
            f.write("SELECT 1;")


def test_combine(cli_runner, tmp_path):
    files = ["test.sql", "folder/other.txt", "bad.py"]
    _create_files(tmp_path, files)
    result = cli_runner.invoke(
        app,
        [
            str(tmp_path.absolute()),
            "-e",
            "txt",
            "-e",
            "sql",
            "-t",
            str((tmp_path / "target.sql").absolute()),
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "Success!"
    with (tmp_path / "target.sql").open() as f:
        assert (
            f.read()
            == """-- other




SELECT 1;


--____________________ End of other ____________________--




-- test




SELECT 1;


--____________________ End of test ____________________--



"""
        )


def test_combine_invalid_sorter(cli_runner):
    result = cli_runner.invoke(app, ["-so", "a"])
    assert result.exit_code == 0
    assert result.output.strip() == "Value Error! sorter a is invalid"


def test_combine_empty_extension(cli_runner):
    result = cli_runner.invoke(app, ["-e", ""])
    assert result.exit_code == 0
    assert (
        result.output.strip() == "Value Error! Extension should not be an empty string"
    )


def test_combine_target_exists(cli_runner, tmp_path):
    _create_files(tmp_path, ["target_exists.sql"])
    result = cli_runner.invoke(
        app,
        [
            str(tmp_path.absolute()),
            "-t",
            str((tmp_path / "target_exists.sql").absolute()),
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "OS Error! Target already exists!"


def test_combine_files_not_found(cli_runner, tmp_path):
    result = cli_runner.invoke(app, [str(tmp_path.absolute()), "-e", "aaa"])
    assert result.exit_code == 0
    assert result.output.strip() == "No files with aaa extension found!"
