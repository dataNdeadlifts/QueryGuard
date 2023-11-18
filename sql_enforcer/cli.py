import typer

from sql_enforcer.engine import RulesEngine

cli = typer.Typer()


@cli.command()  # type: ignore[misc]
def run(path: str) -> None:
    """
    QueryGuardian: A SQL policy enforcer.
    """
    engine = RulesEngine()
    engine.run(path)
