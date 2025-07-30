from pathlib import Path
from typing import Annotated

import rich
import typer
from pydantic import ValidationError

from sql_organizer.combiner import combine_files
from sql_organizer.file import SqlFile
from sql_organizer.file_formatter import get_standard_formatter
from sql_organizer.search import FileExtension, get_all_sql_files
from sql_organizer.sorter import SORTERS, sort_paths

app = typer.Typer()


@app.command()
def combine(
    path: Annotated[
        Path, typer.Argument(help="path, where the SQL files are located")
    ] = Path("."),
    extension: Annotated[list[str], typer.Option("--extension", "-e")] = ["sql"],
    sorters: Annotated[
        list[str],
        typer.Option(
            "--sorter", "-so", help=f"Available sorters: {', '.join(SORTERS)}"
        ),
    ] = [
        "folder",
        "first_number",
    ],
    skip_errors: bool = False,
    uncomment_use: Annotated[bool, typer.Option("--uncomment_use", "-uu")] = False,
    target: Annotated[Path, typer.Option("--target", "-t")] = Path("./target.sql"),
    overwrite: bool = False,
) -> None:
    for sorter in sorters:
        if sorter not in SORTERS:
            rich.print(
                f"[bold red]Value Error![/bold red] sorter [bold blue]{sorter}\
[/bold blue] is invalid"
            )
            return
    if not overwrite and target.exists():
        rich.print("[bold red]OS Error![/bold red] Target already exists!")
        return
    try:
        extensions = [FileExtension(extension=e) for e in extension]
    except ValidationError:
        rich.print(
            "[bold red]Value Error![/bold red] Extension should not be an empty string"
        )
        return
    files = get_all_sql_files(path, extensions)
    if len(files) == 0:
        rich.print(
            f"[yellow]No files with [bold blue]\
{', '.join(e.extension for e in extensions)}\
[/bold blue] extension{'s' if len(extensions) > 1 else ''} found![/yellow]"
        )
        return
    sorted_files = sort_paths(files, [SORTERS[s] for s in sorters])
    sql_files = []
    for file in sorted_files:
        sql_file = SqlFile.from_path(file)
        if isinstance(sql_file, OSError):
            color = "yellow" if skip_errors else "red"
            rich.print(
                f"[bold {color}]OS Error[/bold {color}] Could not open file {file.absolute()}"
            )
            if not skip_errors:
                return
        sql_files.append(sql_file)

    formatter = get_standard_formatter(uncomment_use)
    combine_files(target, sql_files, formatter)
    rich.print("[bold green]Success![/bold green]")
