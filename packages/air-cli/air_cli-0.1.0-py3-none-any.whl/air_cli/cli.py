"""Console script for air_cli."""

import typer
from rich.console import Console

from air_cli import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for air_cli."""
    console.print("Replace this message by putting your code into "
               "air_cli.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
