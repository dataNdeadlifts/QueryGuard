from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoCreateLogin


class TestNoCreateLogin:
    def test_check_method_1(self) -> None:
        rule = NoCreateLogin()
        statements = SQLParser.get_statements("CREATE LOGIN [test_login] WITH PASSWORD = 'test_password';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoCreateLogin()
        statements = SQLParser.get_statements("EXEC sp_grantlogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoCreateLogin()
        statements = SQLParser.get_statements("EXEC sp_addlogin 'test_login', 'test_password';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoCreateLogin()
        statements = SQLParser.get_statements("EXEC sp_addremotelogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoCreateLogin()
        statement = SQLParser.get_statements("CREATE LOGIN test WITH PASSWORD = 'test';")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
