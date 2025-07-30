from collections.abc import Sequence
from pathlib import Path

from sql_organizer.file import SqlFile
from sql_organizer.file_formatter import SqlFileFormatter


def combine_files(
    new_file_path: Path, files: Sequence[SqlFile], formatter: SqlFileFormatter
):
    with new_file_path.open("w") as f:
        f.write("\n".join(formatter.format_file(f) for f in files))
