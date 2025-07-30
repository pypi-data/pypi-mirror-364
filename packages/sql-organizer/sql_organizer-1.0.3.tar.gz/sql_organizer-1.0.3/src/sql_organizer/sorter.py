import re
from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

NUMBERS_REGEX = re.compile(r"[0-9]+")


class Comparable[CT: Comparable](Protocol):
    def __lt__(self: CT, other: CT, /) -> bool: ...


class SortStrategy[T: Comparable[int | str]](ABC):
    @abstractmethod
    def get_sort_order(self, path: Path) -> T: ...


class FirstNumberSort(SortStrategy[int]):
    def get_sort_order(self, path: Path) -> int:
        matches = NUMBERS_REGEX.findall(path.stem)
        return int(matches[0]) if len(matches) >= 1 else 0


class LastNumberSort(SortStrategy[int]):
    def get_sort_order(self, path: Path) -> int:
        matches = NUMBERS_REGEX.findall(path.stem)
        return int(matches[-1]) if len(matches) >= 1 else 0


class LastFolderSort(SortStrategy[str]):
    def get_sort_order(self, path: Path) -> str:
        return path.parent.name


SORTERS: dict[str, SortStrategy[str | int]] = {
    "first_number": FirstNumberSort(),
    "last_number": LastNumberSort(),
    "folder": LastFolderSort(),
}


def sort_paths(
    paths: Sequence[Path], sorting_strategies: Sequence[SortStrategy[int | str]]
) -> list[Path]:
    assert len(sorting_strategies) >= 1, (
        "Sorting strategies should contain at least 1 value"
    )
    return sorted(
        paths, key=lambda x: tuple(s.get_sort_order(x) for s in sorting_strategies)
    )
