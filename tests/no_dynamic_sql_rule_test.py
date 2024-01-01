from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoDynamicSQL


class TestNoDynamicSQL:
    def test_check_method_1(self) -> None:
        rule = NoDynamicSQL()
        statements = SQLParser.get_statements("EXEC ('SELECT * FROM test_table')")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoDynamicSQL()
        statements = SQLParser.get_statements("EXECUTE sp_executesql 'SELECT * FROM test_table';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoDynamicSQL()
        statement = SQLParser.get_statements("EXEC ('SELECT * FROM test_table')")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
