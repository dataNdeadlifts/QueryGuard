from __future__ import annotations

import logging
from pathlib import Path

import typer
from typing_extensions import Annotated

from queryguard.config import Config
from queryguard.engine import RulesEngine

cli = typer.Typer()


@cli.command()
def run(
    path: Annotated[Path, typer.Argument(help="Path to a file or folder containing sql queries")],
    settings: Annotated[str, typer.Option(help="Path to configuration file", show_default=False)] = "",
    select: Annotated[str, typer.Option(help="Select rules to enable", show_default=False)] = "",
    ignore: Annotated[str, typer.Option(help="Ignore rules", show_default=False)] = "",
    debug: Annotated[bool, typer.Option(help="Ignore rules", show_default=False)] = False,
) -> None:
    """QueryGuard: A SQL Policy Guardian."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    cli_arguments = {
        "path": path,
        "settings": settings,
        "select": select,
        "ignore": ignore,
        "debug": debug if debug else None,
    }
    config = Config(cli_arguments)
    logging.basicConfig(level=logging.DEBUG if config.debug else logging.INFO, force=True)  # type: ignore[attr-defined]
    engine = RulesEngine(config)
    engine.run(path)
