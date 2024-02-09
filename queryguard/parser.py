from __future__ import annotations

import logging
from typing import Generator

import sqlparse

logger = logging.getLogger(__name__)


class SQLParser:
    """Parses SQL queries for analysis."""

    @staticmethod
    def get_all_statements(query: str) -> tuple[sqlparse.sql.Statement]:
        """Parses the given SQL query and returns a tuple of sqlparse.sql.Statement objects.

        Args:
            query (str): The SQL query to parse.

        Returns:
            tuple[sqlparse.sql.Statement]: A tuple of sqlparse.sql.Statement objects.
        """
        logger.debug("Parsing file contents")
        return sqlparse.parse(query)  # type: ignore[no-any-return]

    @staticmethod
    def to_case_insensitive_regex(string: str) -> str:
        """Converts the given string to a case-insensitive regular expression.

        Args:
            string (str): The string to convert.

        Returns:
            str: A case-insensitive regular expression string.
        """
        return "^" + "".join([f"[{char.lower()}{char.upper()}]" if char.isalpha() else char for char in string]) + "$"

    @staticmethod
    def filter_statements(
        statements: sqlparse.sql.Statement | tuple[sqlparse.sql.Statement], ttype: sqlparse.sql.Token, regex: str
    ) -> Generator[sqlparse.sql.Statement, None, None]:
        """Yields statements matching the ttype and value from the given tuple of sqlparse.sql.Statement objects.

        Args:
            statements (sqlparse.sql.Statement | tuple[sqlparse.sql.Statement]):
                A tuple of sqlparse.sql.Statement objects.
            ttype (sqlparse.sql.Token): The type of token to filter by.
            regex (str): A regular expression matching the value representation of the token to filter by.

        Yields:
            Generator[sqlparse.sql.Statement, None, None]: A generator of sqlparse.sql.Statement objects.
        """
        logger.debug(f"Getting statements of type {ttype} and regex {regex}")

        if isinstance(statements, sqlparse.sql.Statement):
            statements = (statements,)

        for statement in statements:
            for token in statement.flatten():
                if token.match(ttype=ttype, values=regex, regex=True):
                    yield statement

    @staticmethod
    def get_procedure_statements(
        statements: sqlparse.sql.Statement | tuple[sqlparse.sql.Statement], procedure: str
    ) -> Generator[sqlparse.sql.Statement, None, None]:
        """Yields procedure calls of the given procedure name from the given tuple of sqlparse.sql.Statement objects.

        Args:
            statements (sqlparse.sql.Statement | tuple[sqlparse.sql.Statement]):
                A tuple of sqlparse.sql.Statement objects.
            procedure (str): The name of the procedure to yield calls for.

        Yields:
            Generator[sqlparse.sql.Statement, None, None]: A generator of sqlparse.sql.Statement objects.
        """
        return SQLParser.filter_statements(
            statements, sqlparse.tokens.Name, SQLParser.to_case_insensitive_regex(procedure)
        )

    @staticmethod
    def get_ddl_statements(
        statements: sqlparse.sql.Statement | tuple[sqlparse.sql.Statement], ddl_type: str
    ) -> Generator[sqlparse.sql.Statement, None, None]:
        """Yields ddl statements of the given type from the given tuple of sqlparse.sql.Statement objects.

        Args:
            statements (sqlparse.sql.Statement | tuple[sqlparse.sql.Statement]):
                A tuple of sqlparse.sql.Statement objects.
            ddl_type (str): The type of DDL statements to yield for.

        Yields:
            Generator[sqlparse.sql.Statement, None, None]: A generator of sqlparse.sql.Statement objects.
        """
        return SQLParser.filter_statements(statements, sqlparse.tokens.DDL, ddl_type)

    @staticmethod
    def get_keyword_statements(
        statements: sqlparse.sql.Statement | tuple[sqlparse.sql.Statement], keyword: str
    ) -> Generator[sqlparse.sql.Statement, None, None]:
        """Yields statements containing the given keyword from the given tuple of sqlparse.sql.Statement objects.

        Args:
            statements (sqlparse.sql.Statement | tuple[sqlparse.sql.Statement]):
                A tuple of sqlparse.sql.Statement objects.
            keyword (str): The type of keyword to yield statements for.

        Yields:
            Generator[sqlparse.sql.Statement, None, None]: A generator of sqlparse.sql.Statement objects.
        """
        return SQLParser.filter_statements(statements, sqlparse.tokens.Keyword, keyword)

    @staticmethod
    def get_token(statement: sqlparse.sql.Statement, ttype: sqlparse.sql.Token, regex: str) -> sqlparse.sql.Token:
        """Returns the first token matching the supplied ttype and regex pattern.

        Args:
            statement (sqlparse.sql.Statement): The Statement object.
            ttype (sqlparse.sql.Token): The class representing token type.
            regex (str): A regular expression matching the value representation of the token.

        Returns:
            sqlparse.sql.Token: The first Token object in the statement matching the type and value.
        """
        logger.debug(f"Getting token of type {type} and regex {regex}")

        for token in statement.flatten():
            if token.match(ttype=ttype, values=regex, regex=True):
                return token

    @staticmethod
    def get_procedure_token(statement: sqlparse.sql.Statement, procedure: str) -> sqlparse.sql.Token:
        """Returns the token containing the supplied procedure.

        Args:
            statement (sqlparse.sql.Statement): The Statement object.
            procedure (str): The case-insensitve name of the procedure/function.

        Returns:
            sqlparse.sql.Token: The first Token object in the statement matching the type and value.
        """
        return SQLParser.get_token(statement, sqlparse.tokens.Name, SQLParser.to_case_insensitive_regex(procedure))

    @staticmethod
    def get_ddl_token(statement: sqlparse.sql.Statement, ddl_type: str) -> sqlparse.sql.Token:
        """Returns the token containing the DDL type.

        Args:
            statement (sqlparse.sql.Statement): The Statement object.
            ddl_type (str): A regular expression matching the value representation of the token.

        Returns:
            sqlparse.sql.Token: The first Token object in the statement matching the type and value.
        """
        return SQLParser.get_token(statement, sqlparse.tokens.DDL, ddl_type)

    @staticmethod
    def get_keyword_token(statement: sqlparse.sql.Statement, keyword: str) -> sqlparse.sql.Token:
        """Returns the token matching the supplied keyword.

        Args:
            statement (sqlparse.sql.Statement): The Statement object.
            keyword (str): A regular expression matching the value representation of the token.

        Returns:
            sqlparse.sql.Token: The first Token object in the statement matching the type and value.
        """
        return SQLParser.get_token(statement, sqlparse.tokens.Keyword, keyword)

    @staticmethod
    def get_next_token(statement: sqlparse.sql.Statement, token: sqlparse.sql.Token) -> sqlparse.sql.Token | None:
        """Returns the next token after the given token in the given statement.

        Args:
            statement (sqlparse.sql.Statement): The Statement object.
            token (sqlparse.sql.Token): The Token object.

        Returns:
            sqlparse.sql.Token: A Token object representing the next non-whitespace token.
        """
        logger.debug(f"Getting next token for {token}")

        match = False
        for item in statement.flatten():
            if item.is_whitespace:
                continue
            if item == token:
                match = True
                continue
            if match:
                return item

        return None
