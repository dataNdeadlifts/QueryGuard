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

from QueryGuard import rules
from QueryGuard.config import Config
from QueryGuard.exceptions import RuleViolation
from QueryGuard.parser import SQLParser

logger = logging.getLogger(__name__)


class File:
    """Represents a file to be evaluated against a set of rules.

    Attributes:
        path (Path): The path to the file.
        violations (list[RuleViolation]): A list of rule violations found in the file.
        status (str): The evaluation status of the file.
    """

    def __init__(self, path: Path) -> None:
        """Initializes a new instance of the Engine class.

        Args:
            path (Path): The path to the file to be analyzed.
        """
        self.path = path
        self.violations: list[RuleViolation] = []
        self.status = "Not Run"

    def __repr__(self) -> str:
        return f"File(path={self.path}, status={self.status})"

    def evaluate(self, rules: list[type[rules.BaseRule]]) -> None:
        """Evaluates the file against a list of rules.

        Args:
            rules (list[type[rules.BaseRule]]): A list of rule classes to be evaluated.

        Returns:
            None
        """
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
    """The RulesEngine class represents the engine that runs the rules on SQL files.

    Attributes:
        rules (list[type[rules.BaseRule]]): A list of subclasses of BaseRule.
    """

    def __init__(self, config: Config) -> None:
        """Initializes the QueryGuard engine."""
        self.config = config
        self.rules: list[type[rules.BaseRule]] = [
            x  # type: ignore[type-abstract]
            for x in rules.BaseRule.__subclasses__()
            if x.id in self.config.enabled_rules  # type: ignore[comparison-overlap]
        ]
        logger.debug(f"Enabled rules: {self.config.enabled_rules}")

    def __repr__(self) -> str:
        return "RulesEngine()"

    def get_files(self, input_path: Path) -> list[File]:
        """Retrieves a list of File objects from the input path.

        Args:
            input_path (str): The path to the input file or directory.

        Returns:
            list[File]: A list of File objects.
        """
        logger.debug(f"Getting files from {input_path}")
        path = input_path
        files = []
        if path.is_file():
            files.append(File(path))
        elif path.is_dir():
            for file in path.glob("**/*.sql"):
                files.append(File(file))
        else:
            raise click.ClickException(f"Invalid path: {path}")

        return files

    def run(self, input_path: Path) -> None:
        """Evaluates each file in the input path for adherance to the enabled rules.

        Args:
            input_path (str): The path to the input file or directory.

        Returns:
            None
        """
        files = self.get_files(input_path)
        for file in track(files, description="Processing..."):
            file.evaluate(self.rules)
        self.display_results(files)

        for file in files:
            if file.violations:
                sys.exit(1)

    def display_results(self, files: list[File]) -> None:
        """Displays the results of the rule evaluation.

        Args:
            files (list[File]): A list of File objects.

        Returns:
            None
        """
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
                    table.add_row("", "", str(violation), Syntax(violation.statement, "sql", theme="ansi_dark"))

        console.print(table)
