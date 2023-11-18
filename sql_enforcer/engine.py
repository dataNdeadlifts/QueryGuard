from __future__ import annotations

import logging
import sys
from pathlib import Path

import click
import sqlparse
from rich.console import Console
from rich.progress import track
from rich.syntax import Syntax
from rich.table import Table

from sql_enforcer import rules
from sql_enforcer.exceptions import RuleViolation
from sql_enforcer.parser import SQLParser

logger = logging.getLogger(__name__)


class File:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.violations: list[RuleViolation] = []
        self.status = "Not Run"

    def __repr__(self) -> str:
        return f"File(path={self.path}, status={self.status})"

    def evaluate(self, rules: list[type[rules.BaseRule]]) -> None:
        logger.debug(f"Evaluating rules against {self.path}")
        statements: tuple[sqlparse.sql.Statement] = SQLParser.get_statements(self.path.read_text())
        for rule in rules:
            try:
                rule().check(statements)
            except RuleViolation as e:
                self.violations.append(e)

        if self.violations:
            self.status = "Failed ❌"
        else:
            self.status = "Passed ✅"


class RulesEngine:
    def __init__(self) -> None:
        self.rules: list[type[rules.BaseRule]] = rules.BaseRule.__subclasses__()

    def __repr__(self) -> str:
        return "RulesEngine()"

    def get_files(self, input_path: str) -> list[File]:
        logger.debug(f"Getting files from {input_path}")
        path = Path(input_path)
        files = []
        if path.is_file():
            files.append(File(path))
        elif path.is_dir():
            for file in path.glob("**/*.sql"):
                files.append(File(file))
        else:
            raise click.ClickException(f"Invalid path: {path}")

        return files

    def run(self, input_path: str) -> None:
        files = self.get_files(input_path)
        for file in track(files, description="Processing..."):
            file.evaluate(self.rules)
        self.display_results(files)

        for file in files:
            if file.violations:
                sys.exit(1)

    def display_results(self, files: list[File]) -> None:
        logger.debug("Displaying results")
        console = Console()
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("File")
        table.add_column("Status")
        table.add_column("Violations")
        table.add_column("Statements")

        for file in files:
            table.add_section()
            if file.status == "Passed ✅":
                table.add_row(str(file.path), "Passed ✅", "", "")
            elif file.status == "Not Run":
                table.add_row(str(file.path), "Not Run", "", "")
            else:
                table.add_row(str(file.path), "Failed ❌", "", "")
                for violation in file.violations:
                    table.add_row("", "", str(violation.rule), Syntax(violation.statement, "sql", theme="ansi_dark"))

        console.print(table)
