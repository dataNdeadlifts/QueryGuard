import typer

from QueryGuard.engine import RulesEngine

cli = typer.Typer()


@cli.command()  # type: ignore[misc]
def run(path: str) -> None:
    """QueryGuard: A SQL policy guardian."""
    engine = RulesEngine()
    engine.run(path)
