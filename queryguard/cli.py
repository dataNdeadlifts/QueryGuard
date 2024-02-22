from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, cast

import typer

from queryguard import __version__, config
from queryguard.engine import RulesEngine
from queryguard.exceptions import TerminatingError

cli = typer.Typer()


@cli.command(help="QueryGuard: A guard against unruly sql.")
def run(
    path: Optional[Path] = typer.Argument(default=None, help="Path to a file or folder containing sql queries."),  # noqa: B008  , UP007 # workaround for defects in typer using optional arguments
    settings: Optional[str] = typer.Option(default="", help="Path to configuration file."),  # noqa: UP007
    select: Optional[str] = typer.Option(default=config.SelectSetting.default, help="Rules to enable."),  # noqa: UP007
    ignore: Optional[str] = typer.Option(default=config.IgnoreSetting.default, help="Rules to ignore."),  # noqa: UP007
    output: Optional[str] = typer.Option(default=config.OutputSetting.default, help="Output format."),  # noqa: UP007
    version: Optional[bool] = typer.Option(default=False, help="Print the version and exit."),  # noqa: UP007
    debug: Optional[bool] = typer.Option(default=config.DebugSetting.default, help="Enable debug logging."),  # noqa: UP007
) -> None:
    """Run the QueryGuard tool with the specified parameters.

    Args:
        path (Path): Path to a file or folder containing SQL queries.
        settings (str, optional): Path to configuration file. Defaults to "".
        select (str, optional): Select rules to enable. Defaults to config.SelectSetting.default.
        ignore (str, optional): Ignore rules. Defaults to config.IgnoreSetting.default.
        output (str, optional): Output format. Defaults to config.OutputSetting.default.
        version (bool, optional): Print the version and exit. Defaults to False.
        debug (bool, optional): Enable debug mode. Defaults to config.DebugSetting.default.

    Returns:
        None
    """
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO, force=True)

    if version:
        typer.echo(__version__)
        raise typer.Exit()

    if not path:
        typer.echo("Error: Missing argument 'path'.")
        typer.echo("For usage information, use the --help flag.")
        raise typer.Exit(code=2)

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
    try:
        RulesEngine(request_params).run()
    except TerminatingError as err:
        raise typer.Exit(code=err.exit_code) from err
