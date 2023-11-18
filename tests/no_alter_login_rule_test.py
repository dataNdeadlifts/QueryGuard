import pytest

from sql_enforcer.exceptions import RuleViolation
from sql_enforcer.parser import SQLParser
from sql_enforcer.rules import NoAlterLoginRule


class TestNoAlterLoginRule:
    def test_check_method_1(self) -> None:
        rule = NoAlterLoginRule()
        statements = SQLParser.get_statements("ALTER LOGIN [test_login] ENABLE;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoAlterLoginRule()
        statements = SQLParser.get_statements("EXEC sp_denylogin 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoAlterLoginRule()
        statements = SQLParser.get_statements("EXEC sp_change_users_login 'Update_One', 'test_login', 'test_user';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoAlterLoginRule()
        statements = SQLParser.get_statements(
            "EXEC sp_change_users_login 'Auto_Fix', \
                                              'test_login', NULL, 'test_password';"
        )
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_5(self) -> None:
        rule = NoAlterLoginRule()
        statements = SQLParser.get_statements("EXEC sp_password 'old_password', 'new_password', 'test_login';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoAlterLoginRule()
        statement = SQLParser.get_statements("ALTER LOGIN [test_login] ENABLE;")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
