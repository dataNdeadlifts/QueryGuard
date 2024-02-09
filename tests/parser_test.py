from __future__ import annotations

import sqlparse

from queryguard.parser import SQLParser


class TestParser:
    def test_file_evaluate_no_violations(self) -> None:
        statements = SQLParser.get_all_statements("select 1")
        SQLParser.filter_statements(statements[0], sqlparse.sql.Token, "1")
