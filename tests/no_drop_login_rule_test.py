from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoDropLogin


class TestNoDropLogin:
    def test_check_method_1(self) -> None:
        rule = NoDropLogin()
        statements = SQLParser.get_all_statements("DROP LOGIN [test_login];")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoDropLogin()
        statements = SQLParser.get_all_statements("EXEC sp_droplogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoDropLogin()
        statements = SQLParser.get_all_statements("EXEC sp_dropremotelogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoDropLogin()
        statements = SQLParser.get_all_statements("EXEC sp_revokelogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_5(self) -> None:
        rule = NoDropLogin()
        statements = SQLParser.get_all_statements(
            "IF EXISTS (SELECT * FROM master.sys.server_principals \
                                              WHERE name = 'shenanigans')\n\
                                              DROP LOGIN shenanigans\n\
                                              GO"
        )
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoDropLogin()
        statement = SQLParser.get_all_statements("DROP LOGIN [test_login];")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
