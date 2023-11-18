import pytest

from QueryGuard.exceptions import RuleViolation
from QueryGuard.parser import SQLParser
from QueryGuard.rules import NoCreateLoginRule


class TestNoCreateLoginRule:
    def test_check_method_1(self) -> None:
        rule = NoCreateLoginRule()
        statements = SQLParser.get_statements("CREATE LOGIN [test_login] WITH PASSWORD = 'test_password';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoCreateLoginRule()
        statements = SQLParser.get_statements("EXEC sp_grantlogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoCreateLoginRule()
        statements = SQLParser.get_statements("EXEC sp_addlogin 'test_login', 'test_password';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoCreateLoginRule()
        statements = SQLParser.get_statements("EXEC sp_addremotelogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoCreateLoginRule()
        statement = SQLParser.get_statements("CREATE LOGIN test WITH PASSWORD = 'test';")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
