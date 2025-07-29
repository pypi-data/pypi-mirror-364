from typing import Optional
import typer
from scimon import __app_name__, __version__
from scimon.scimon import reproduce as r
import os
app = typer.Typer()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(version: Optional[bool] = typer.Option(
    None,
    "--version",
    "-v",
    help="Display the application's version and exit",
    callback=_version_callback,
    is_eager=True
)) -> None:
    return

@app.command(help="Generates a Makefile for reproducing the supplied file at a given version specified with the git commit hash.")
def reproduce(
    file: str = typer.Argument(help="Path to the file to reproduce"),
    git_hash: Optional[str] = typer.Option(None, "--git-hash", "-g", help="Git commit hash of the version to reproduce, selects newest version by default")
) -> None:
    r(file, git_hash)

@app.command(help="Initialize the current working directory for monitoring")
def init() -> None:
    # Adds cwd to ~/.scimon/.autogitcheck
    # TODO
    pass

@app.command(help="Lists all directories currently being monitored")
def list() -> None:
    # TODO
    pass

@app.command(help="Removes a directory from being monitored")
def remove(dir: str = typer.Argument(help="Directory to remove", default=os.getcwd())) -> None:
    # TODO
    pass