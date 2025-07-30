from pathlib import Path

from pydantic import BaseModel, Field


class SqlFile(BaseModel, frozen=True):
    file_name: str = Field(min_length=1)
    sql_text: str

    @classmethod
    def from_path(cls, path: Path) -> "OSError | SqlFile":
        file_name = path.stem
        try:
            with path.open("r") as f:
                sql_text = f.read()
        except OSError as e:
            return e
        return SqlFile(file_name=file_name, sql_text=sql_text)
