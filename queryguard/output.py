from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, TypeVar

from rich import progress
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from queryguard.exceptions import TerminatingError
from queryguard.files import File, FileEncoder

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseOutputHandler(ABC):
    """Base class for handling results."""

    @property
    @abstractmethod
    def id(self) -> str:
        """ID of the output handler."""

    @abstractmethod
    def track(self, iterable: Iterable[T], description: str) -> Iterable[T]:
        """Track progress by iterating over a sequence.

        Args:
            iterable (list[File]): A list of files that have been analyzed.
            description (str): A description of the progress.
        """
        pass  # pragma: no cover

    @abstractmethod
    def process_result(self, files: list[File]) -> None:
        """Processes the execution result, typically sending it to a consumer like standard out or a different system.

        Args:
            files (list[File]): A list of files that have been analyzed.

        Returns:
            None
        """
        pass  # pragma: no cover

    def exit_violation_found(self) -> None:
        """Ends execution when a violdation was found."""
        raise TerminatingError(exit_code=1)

    def exit_violation_not_found(self) -> None:
        """Ends execution when no violdation was found."""
        raise TerminatingError()


class ConsoleText(BaseOutputHandler):
    """Concrete class for sending results as text to stdout."""

    id = "text"

    def __init__(self) -> None:
        """Initializes the ConsoleJson class."""
        self.console = Console()

    def track(self, iterable: Iterable[T], description: str = "Processing...") -> Any:  # noqa: ANN401
        """Track progress by iterating over a sequence using the rich.progress.track function.

        Args:
            iterable (list[File]): A list of files that have been analyzed.
            description (str): A description of the progress.
        """
        return progress.track(iterable, description)

    def process_result(self, files: list[File]) -> None:
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
            else:
                table.add_row(str(file.path), "Failed ❌", "", "")
                for violation in file.violations:
                    cleaned_statement = (
                        violation.statement.strip()
                        .removeprefix("go")
                        .removeprefix("GO")
                        .removesuffix("go")
                        .removesuffix("GO")
                        .strip()
                    )
                    table.add_row("", "", str(violation), Syntax(cleaned_statement, "sql", theme="ansi_dark"))

        console.print(table)


class ConsoleJson(BaseOutputHandler):
    """Concrete class for sending results as text to stdout."""

    id = "json"

    def __init__(self) -> None:
        """Initializes the ConsoleJson class."""
        self.console = Console()

    def track(self, iterable: Iterable[T], description: str = "") -> Iterable[T]:
        """Stub for satisfying the HandlerInterface.

        Args:
            iterable (list[File]): A list of files that have been analyzed.
            description (str): A description of the progress.
        """
        return iterable

    def process_result(self, files: list[File]) -> None:
        """Displays the results of the rule evaluation.

        Args:
            files (list[File]): A list of File objects.

        Returns:
            None
        """
        logger.debug("Displaying results")
        files_json = json.dumps(files, cls=FileEncoder, indent=4)
        self.console.print(files_json)
