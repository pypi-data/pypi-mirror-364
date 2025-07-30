from sql_organizer.file import SqlFile


def test_sql_file_from_path(tmp_path):
    with open(tmp_path / "sql_file_test.sql", "w", encoding="utf-8") as f:
        f.write("SELECT 1;")
    sql_file = SqlFile.from_path(tmp_path / "sql_file_test.sql")
    assert isinstance(sql_file, SqlFile)
    assert sql_file.file_name == "sql_file_test"
    assert sql_file.sql_text == "SELECT 1;"


def test_sql_file_from_path_no_file(tmp_path):
    sql_file = SqlFile.from_path(tmp_path / "no_file.sql")
    assert isinstance(sql_file, OSError)
