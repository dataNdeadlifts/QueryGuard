import sqlparse


class RuleViolation(Exception):
    """Exception raised when a query does not adhere to the ruleset.

    Attributes:
        rule (str): The rule that was violated.
        statement (str): The statement that caused the violation.
        message (str): The error message that will be displayed.
    """

    def __init__(self, rule: str, statement: sqlparse.sql.Statement) -> None:
        self.rule = rule
        self.statement = str(statement)[0:50]
        self.message = f"Violated rule {self.rule}. Statement: '{str(statement)[0:50]}'"
        super().__init__(self.message)
