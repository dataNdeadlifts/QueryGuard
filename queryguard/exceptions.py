from __future__ import annotations

import sqlparse


class TerminatingError(Exception):
    """Exception that will stop QueryGuard execution."""

    def __init__(self, exit_code: int = 0) -> None:
        """Initialize a TerminatingError Exception object.

        Args:
            exit_code (int): The exit code to use upon sys.exit.
        """
        self.exit_code = exit_code

    pass


class RuleViolation(Exception):
    """Exception raised when a query does not adhere to the ruleset.

    Attributes:
        rule (str): The rule that was violated.
        statement (str): The statement that caused the violation.
        message (str): The error message that will be displayed.
    """

    def __init__(self, rule: str, id: str, statement: sqlparse.sql.Statement) -> None:
        """Initialize a RuleViolation Exception object.

        Args:
            rule (str): The rule that was violated.
            id (str): The id of the rule that was violated.
            statement (sqlparse.sql.Statement): The SQL statement that violated the rule.
        """
        self.rule = rule
        self.id = id
        self.statement = str(statement)[0:50]
        self.message = f"Violated rule {self.rule} ({self.id}). Statement: '{str(statement)[0:50]}'"
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.rule} ({self.id})"
