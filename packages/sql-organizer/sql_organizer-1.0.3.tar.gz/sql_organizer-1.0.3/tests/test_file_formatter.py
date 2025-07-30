import pytest

from sql_organizer.file import SqlFile
from sql_organizer.file_formatter import (
    BreakLine,
    FormatterCombination,
    NameFormatter,
    PlainSqlText,
    SkipLine,
    UseCommentRemover,
)


@pytest.fixture(scope="module")
def sql_file() -> SqlFile:
    return SqlFile(
        file_name="100_DEPLOYMENT",
        sql_text="-- use ROLE ACCOUNTADMIN;\n-- USE SCHEMA LZ_D_SYSTEM;\
\n\nCREATE TABLE TABLE1;",
    )


def test_name_formatter(sql_file):
    assert NameFormatter().format_file(sql_file) == "-- 100_DEPLOYMENT"


def test_skip_line(sql_file):
    assert SkipLine().format_file(sql_file) == "\n"


def test_plain_sql_text(sql_file):
    assert (
        PlainSqlText().format_file(sql_file)
        == "-- use ROLE ACCOUNTADMIN;\n\
-- USE SCHEMA LZ_D_SYSTEM;\n\nCREATE TABLE TABLE1;"
    )


def test_break_line(sql_file):
    assert (
        BreakLine().format_file(sql_file)
        == "--" + "_" * 20 + " End of 100_DEPLOYMENT " + "_" * 20 + "--"
    )


def test_use_comment_remover(sql_file):
    assert (
        UseCommentRemover(formatter=PlainSqlText()).format_file(sql_file)
        == "USE ROLE ACCOUNTADMIN;\nUSE SCHEMA LZ_D_SYSTEM;\n\nCREATE TABLE TABLE1;"
    )


def test_formatter_combination(sql_file):
    assert (
        FormatterCombination(formatters=(NameFormatter(), NameFormatter())).format_file(
            sql_file
        )
        == "-- 100_DEPLOYMENT\n-- 100_DEPLOYMENT"
    )
