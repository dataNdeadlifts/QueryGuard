from __future__ import annotations

import logging
from pathlib import Path
from typing import cast

import typer
from typing_extensions import Annotated

from queryguard import config
from queryguard.engine import RulesEngine

cli = typer.Typer()


@cli.command()
def run(
    path: Annotated[Path, typer.Argument(help="Path to a file or folder containing sql queries")],
    settings: Annotated[str, typer.Option(help="Path to configuration file", show_default=False)] = "",
    select: Annotated[
        str, typer.Option(help="Select rules to enable", show_default=False)
    ] = config.SelectSetting.default,
    ignore: Annotated[str, typer.Option(help="Ignore rules", show_default=False)] = config.IgnoreSetting.default,
    output: Annotated[str, typer.Option(help="Output format", show_default=True)] = config.OutputSetting.default,
    debug: Annotated[bool, typer.Option(help="Ignore rules", show_default=False)] = config.DebugSetting.default,
) -> None:
    """QueryGuard: A SQL Policy Guardian."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, force=True)
    request_params = cast(
        config.RequestParams,
        {
            "path": path,
            "settings": settings,
            "select": select,
            "ignore": ignore,
            "output": output,
            "debug": debug if debug else None,
        },
    )
    RulesEngine(request_params).run()
