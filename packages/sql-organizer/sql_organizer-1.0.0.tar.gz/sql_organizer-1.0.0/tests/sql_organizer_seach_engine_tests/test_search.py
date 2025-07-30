from collections.abc import Sequence
from pathlib import Path

import pytest
from pydantic import ValidationError

from sql_organizer_search_engine.search import FileExtension, get_all_sql_files


def test_file_extension_min_length():
    with pytest.raises(ValidationError):
        FileExtension(extension="")


def test_get_glob_returns_correct_pattern():
    ext = FileExtension(extension="sql")
    assert ext.get_glob() == "**/*.sql"
    ext2 = FileExtension(extension="txt")
    assert ext2.get_glob() == "**/*.txt"


def _create_files(tmp_path: Path, files: Sequence[str]):
    for file in files:
        (tmp_path / file).mkdir(parents=True, exist_ok=True)


def test_get_all_sql_files(tmp_path):
    files = ["b.sql", "a.sql", "folder/c.sql", "p.txt"]
    extensions = [FileExtension(extension="sql")]
    _create_files(tmp_path, files)
    sql_files = get_all_sql_files(tmp_path, extensions)
    assert set(sql_files) == {
        tmp_path / "b.sql",
        tmp_path / "a.sql",
        tmp_path / "folder/c.sql",
    }


def test_get_all_sql_files_extensions_error():
    with pytest.raises(AssertionError):
        get_all_sql_files(Path("."), [])
