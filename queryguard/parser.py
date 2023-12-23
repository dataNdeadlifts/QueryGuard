from __future__ import annotations

import logging
from typing import Generator

import sqlparse

logger = logging.getLogger(__name__)


class SQLParser:
    """Parses SQL queries for analysis."""

    @staticmethod
    def get_statements(query: str) -> tuple[sqlparse.sql.Statement]:
        """Parses the given SQL query and returns a tuple of sqlparse.sql.Statement objects.

        Args:
            query (str): The SQL query to parse.

        Returns:
            tuple[sqlparse.sql.Statement]: A tuple of sqlparse.sql.Statement objects.
        """
        logger.debug("Parsing file contents")
        return sqlparse.parse(query)  # type: ignore[no-any-return]

    @staticmethod
    def _to_case_insensitive_regex(string: str) -> str:
        """Converts the given string to a case-insensitive regular expression.

        Args:
            string (str): The string to convert.

        Returns:
            str: A case-insensitive regular expression string.
        """
        return "^" + "".join([f"[{char}{char.upper()}]" if char.isalpha() else char for char in string]) + "$"

    @staticmethod
    def get_ddl_statements(
        statements: tuple[sqlparse.sql.Statement], type: str
    ) -> Generator[sqlparse.sql.Statement, None, None]:
        """Yields DDL statements of the given type from the given tuple of sqlparse.sql.Statement objects.

        Args:
            statements (tuple[sqlparse.sql.Statement]): A tuple of sqlparse.sql.Statement objects.
            type (str): The type of DDL statement to yield.

        Yields:
            Generator[sqlparse.sql.Statement, None, None]: A generator of sqlparse.sql.Statement objects.
        """
        logger.debug(f"Getting DDL statements of type {type}")
        for item in statements:
            if item.is_group:
                yield from SQLParser.get_ddl_statements(item.tokens, type)

            if item.match(
                sqlparse.tokens.DDL,
                SQLParser._to_case_insensitive_regex(type),
                regex=True,
            ):
                yield item.parent

    @staticmethod
    def get_exec_string(statements: tuple[sqlparse.sql.Statement]) -> Generator[sqlparse.sql.Statement, None, None]:
        """Yields EXEC statements from the given tuple of sqlparse.sql.Statement objects.

        Args:
            statements (tuple[sqlparse.sql.Statement]): A tuple of sqlparse.sql.Statement objects.

        Yields:
            Generator[sqlparse.sql.Statement, None, None]: A generator of sqlparse.sql.Statement objects.
        """
        logger.debug("Getting EXEC statements")

        exec_match = False

        for item in statements:
            if item.is_group:
                yield from SQLParser.get_exec_string(item.tokens)

            if exec_match and item.is_whitespace:
                continue

            if item.match(
                sqlparse.tokens.Keyword,
                SQLParser._to_case_insensitive_regex("exec"),
                regex=True,
            ):
                exec_match = True
                continue

            if exec_match and isinstance(item, sqlparse.sql.Parenthesis):
                exec_match = False
                yield item.parent

    @staticmethod
    def get_procedure_calls(
        statements: tuple[sqlparse.sql.Statement], procedure: str
    ) -> Generator[sqlparse.sql.Statement, None, None]:
        """Yields procedure calls of the given procedure name from the given tuple of sqlparse.sql.Statement objects.

        Args:
            statements (tuple[sqlparse.sql.Statement]): A tuple of sqlparse.sql.Statement objects.
            procedure (str): The name of the procedure to yield calls for.

        Yields:
            Generator[sqlparse.sql.Statement, None, None]: A generator of sqlparse.sql.Statement objects.
        """
        logger.debug(f"Getting procedure calls for {procedure}")

        for item in statements:
            if item.is_group:
                yield from SQLParser.get_procedure_calls(item.tokens, procedure)

            if item.match(
                sqlparse.tokens.Name,
                SQLParser._to_case_insensitive_regex(procedure),
                regex=True,
            ):
                yield item.parent.parent

    @staticmethod
    def acts_on_type(statement: sqlparse.sql.Statement, type: str) -> bool:
        """Determines if the given sqlparse.sql.Statement object acts on the given type.

        Args:
            statement (sqlparse.sql.Statement): The sqlparse.sql.Statement object to check.
            type (str): The type to check for.

        Returns:
            bool: True if the statement acts on the given type, False otherwise.
        """
        logger.debug(f"Checking if statement acts on type {type}")

        for token in statement.tokens:
            if token.is_group:
                result = SQLParser.acts_on_type(token, type)
                if result:
                    return True
            if token.match(
                sqlparse.tokens.Name,
                SQLParser._to_case_insensitive_regex(type),
                regex=True,
            ) or token.match(
                sqlparse.tokens.Keyword,
                SQLParser._to_case_insensitive_regex(type),
                regex=True,
            ):
                return True
        return False
