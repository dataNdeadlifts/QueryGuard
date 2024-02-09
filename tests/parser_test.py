from __future__ import annotations

import sqlparse

from queryguard.parser import SQLParser


class TestParser:
    def test_single_statement(self) -> None:
        statements = SQLParser.get_all_statements("select 1")
        list(SQLParser.filter_statements(statements[0], sqlparse.sql.Token, "1"))

    def test_no_next_token(self) -> None:
        statements = SQLParser.get_all_statements("select 1")
        token = statements[0].tokens[-1]
        next_token = SQLParser.get_next_token(statements[0], token)
        assert next_token is None
