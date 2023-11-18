import pytest

from sql_enforcer.exceptions import RuleViolation
from sql_enforcer.parser import SQLParser
from sql_enforcer.rules import NoDynamicSQLRule


class TestNoDynamicSQLRule:
    def test_check_method_1(self) -> None:
        rule = NoDynamicSQLRule()
        statements = SQLParser.get_statements("EXEC ('SELECT * FROM test_table')")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoDynamicSQLRule()
        statements = SQLParser.get_statements("EXECUTE sp_executesql 'SELECT * FROM test_table';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoDynamicSQLRule()
        statement = SQLParser.get_statements("EXEC ('SELECT * FROM test_table')")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
