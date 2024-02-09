from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoAlterLogin


class TestNoAlterLogin:
    def test_check_method_1(self) -> None:
        rule = NoAlterLogin()
        statements = SQLParser.get_all_statements("ALTER LOGIN [test_login] ENABLE;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoAlterLogin()
        statements = SQLParser.get_all_statements("EXEC sp_denylogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoAlterLogin()
        statements = SQLParser.get_all_statements("EXEC sp_change_users_login 'Update_One', 'test_login', 'test_user';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoAlterLogin()
        statements = SQLParser.get_all_statements(
            "EXEC sp_change_users_login 'Auto_Fix', \
                                              'test_login', NULL, 'test_password';"
        )
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_5(self) -> None:
        rule = NoAlterLogin()
        statements = SQLParser.get_all_statements("EXEC sp_password 'old_password', 'new_password', 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_6(self) -> None:
        rule = NoAlterLogin()
        statements = SQLParser.get_all_statements("EXEC sp_defaultdb 'test_login', 'test_database';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_7(self) -> None:
        rule = NoAlterLogin()
        statements = SQLParser.get_all_statements("EXEC sp_defaultlanguage 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoAlterLogin()
        statement = SQLParser.get_all_statements("ALTER LOGIN [test_login] ENABLE;")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
