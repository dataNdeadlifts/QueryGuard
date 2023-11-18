import pytest

from QueryGuard.exceptions import RuleViolation
from QueryGuard.parser import SQLParser
from QueryGuard.rules import NoAlterServerRoleRule


class TestNoAlterServerRoleRule:
    def test_check_method_1(self) -> None:
        rule = NoAlterServerRoleRule()
        statements = SQLParser.get_statements("ALTER SERVER ROLE test_role ADD MEMBER test_login;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoAlterServerRoleRule()
        statements = SQLParser.get_statements("sp_addsrvrolemember 'test_login', 'test_role';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoAlterServerRoleRule()
        statements = SQLParser.get_statements("sp_dropsrvrolemember 'test_login', 'test_role';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_database_role(self) -> None:
        rule = NoAlterServerRoleRule()
        statements = SQLParser.get_statements("ALTER ROLE test_role ADD MEMBER test_user;")
        rule.check(statements)

    def test_app_role(self) -> None:
        rule = NoAlterServerRoleRule()
        statements = SQLParser.get_statements("ALTER APPLICATION ROLE test_app_role WITH PASSWORD = 'test_password';")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoAlterServerRoleRule()
        statement = SQLParser.get_statements("ALTER SERVER ROLE test_role ADD MEMBER test_login;")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
