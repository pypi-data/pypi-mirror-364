import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sql_organizer_file.file import SqlFile

COMMENT_REGEX = re.compile(r"--\s*use", flags=re.I + re.M)


class SqlFileFormatter(ABC):
    @abstractmethod
    def format_file(self, sql_file: SqlFile) -> str: ...

    def and_(self, formatter: "SqlFileFormatter") -> "FormatterCombination":
        return FormatterCombination(formatters=(self, formatter))


@dataclass(slots=True)
class FormatterCombination(SqlFileFormatter):
    formatters: tuple[SqlFileFormatter, ...]

    def format_file(self, sql_file: SqlFile) -> str:
        return "\n".join(formater.format_file(sql_file) for formater in self.formatters)

    def and_(self, formatter: SqlFileFormatter) -> "FormatterCombination":
        return FormatterCombination(formatters=(*self.formatters, formatter))


class NameFormatter(SqlFileFormatter):
    def format_file(self, sql_file: SqlFile) -> str:
        return f"-- {sql_file.file_name}"


class SkipLine(SqlFileFormatter):
    def format_file(self, sql_file: SqlFile) -> str:
        return "\n"


class PlainSqlText(SqlFileFormatter):
    def format_file(self, sql_file: SqlFile) -> str:
        return sql_file.sql_text


class BreakLine(SqlFileFormatter):
    def format_file(self, sql_file: SqlFile) -> str:
        return "--" + "_" * 20 + f" End of {sql_file.file_name} " + "_" * 20 + "--"


@dataclass(slots=True)
class UseCommentRemover(SqlFileFormatter):
    formatter: SqlFileFormatter

    def format_file(self, sql_file: SqlFile) -> str:
        return COMMENT_REGEX.sub("USE", self.formatter.format_file(sql_file))


def get_standard_formatter(remove_comments: bool) -> SqlFileFormatter:
    return (
        NameFormatter()
        .and_(SkipLine())
        .and_(SkipLine())
        .and_(
            UseCommentRemover(formatter=PlainSqlText())
            if remove_comments
            else PlainSqlText()
        )
        .and_(SkipLine())
        .and_(BreakLine())
        .and_(SkipLine())
        .and_(SkipLine())
    )
