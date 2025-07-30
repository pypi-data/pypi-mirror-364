from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, Field


class FileExtension(BaseModel, frozen=True):
    extension: str = Field(min_length=1)

    def get_glob(self) -> str:
        return f"**/*.{self.extension}"


def get_all_sql_files(path: Path, extensions: Sequence[FileExtension]) -> list[Path]:
    assert len(extensions) >= 1, "Should provide at least 1 extension"
    paths: list[Path] = []
    for extension in extensions:
        paths.extend(path.glob(extension.get_glob()))
    return paths
