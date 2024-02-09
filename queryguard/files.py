from __future__ import annotations

import logging
import re
from json import JSONEncoder
from pathlib import Path
from typing import Any

import sqlparse

from queryguard import rules
from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser

logger = logging.getLogger(__name__)


class FileEncoder(JSONEncoder):
    """Encodes File objects to JSON format."""

    def default(self, obj: Any) -> Any:  # noqa: ANN401
        """Converts the object to a JSON-serializable representation.

        Args:
            obj (Any): The object to be converted.

        Returns:
            Any: The JSON-serializable representation of the object.
        """
        if isinstance(obj, File):
            return {
                "path": str(obj.path),
                "violations": obj.violations,
                "status": re.sub(r"[^\x00-\x7F]", " ", obj.status).strip(),
            }

        if isinstance(obj, RuleViolation):
            return {
                "name": obj.rule,
                "id": obj.id,
                "statement": obj.statement.strip()
                .removeprefix("go")
                .removeprefix("GO")
                .removesuffix("go")
                .removesuffix("GO")
                .strip(),
                "message": obj.message,
            }

        return super().default(obj)  # pragma: no cover


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

        try:
            text = self.path.read_text(encoding="utf-8", errors="strict")
        except UnicodeDecodeError:
            text = self.path.read_text(encoding="utf-16", errors="strict")

        statements: tuple[sqlparse.sql.Statement] = SQLParser.get_all_statements(text)
        for rule in rules:
            try:
                rule().check(statements)
            except RuleViolation as e:
                self.violations.append(e)

        if self.violations:
            self.status = "Failed ❌"
        else:
            self.status = "Passed ✅"
