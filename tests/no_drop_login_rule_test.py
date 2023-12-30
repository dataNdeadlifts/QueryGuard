from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoDropLoginRule


class TestNoDropLoginRule:
    def test_check_method_1(self) -> None:
        rule = NoDropLoginRule()
        statements = SQLParser.get_statements("DROP LOGIN [test_login];")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoDropLoginRule()
        statements = SQLParser.get_statements("EXEC sp_droplogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoDropLoginRule()
        statements = SQLParser.get_statements("EXEC sp_dropremotelogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoDropLoginRule()
        statements = SQLParser.get_statements("EXEC sp_revokelogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoDropLoginRule()
        statement = SQLParser.get_statements("DROP LOGIN [test_login];")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
