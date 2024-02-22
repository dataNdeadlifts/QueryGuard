import typer

from queryguard.cli import cli

__version__ = "0.5.0-beta.1"

if __name__ == "__main__":
    typer.run(cli())
