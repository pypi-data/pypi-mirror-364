from pathlib import Path

import pytest

from sql_organizer.sorter import (
    FirstNumberSort,
    LastFolderSort,
    LastNumberSort,
    sort_paths,
)


@pytest.mark.parametrize(
    ["path", "result"],
    [
        [Path("100_DEPLOY.sql"), 100],
        [Path("20_DEPLOY_3.sql"), 20],
        [Path("NO_TEXT.sql"), 0],
    ],
)
def test_first_number_sort(path, result):
    first_number_sorter = FirstNumberSort()
    assert first_number_sorter.get_sort_order(path) == result


@pytest.mark.parametrize(
    ["path", "result"],
    [
        [Path("100_DEPLOY.sql"), 100],
        [Path("20_DEPLOY_3.sql"), 3],
        [Path("NO_TEXT.sql"), 0],
    ],
)
def test_last_number_sort(path, result):
    last_number_sorter = LastNumberSort()
    assert last_number_sorter.get_sort_order(path) == result


def test_last_folder_sort():
    last_folder_sorter = LastFolderSort()
    assert (
        last_folder_sorter.get_sort_order(Path("root/folder_name/100_DEPLOY.sql"))
        == "folder_name"
    )


def test_sort_paths():
    paths = [
        Path("150_20_DEPLOY.sql"),
        Path("100_DEPLOY.sql"),
        Path("200_DEPLOY.sql"),
        Path("150_10_DEPLOY.sql"),
    ]
    sorters = [FirstNumberSort(), LastNumberSort()]
    assert sort_paths(paths, sorters) == [
        Path("100_DEPLOY.sql"),
        Path("150_10_DEPLOY.sql"),
        Path("150_20_DEPLOY.sql"),
        Path("200_DEPLOY.sql"),
    ]


def test_sort_paths_with_folders():
    paths = [
        Path("B/300_DEPLOY.sql"),
        Path("A/100_DEPLOY.sql"),
        Path("B/150_DEPLOY.sql"),
        Path("A/200_DEPLOY.sql"),
    ]
    sorters = [LastFolderSort(), FirstNumberSort()]
    assert sort_paths(paths, sorters) == [
        Path("A/100_DEPLOY.sql"),
        Path("A/200_DEPLOY.sql"),
        Path("B/150_DEPLOY.sql"),
        Path("B/300_DEPLOY.sql"),
    ]


def test_sort_paths_error():
    with pytest.raises(AssertionError):
        sort_paths([], [])
