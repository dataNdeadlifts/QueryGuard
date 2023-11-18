import pytest

from sql_enforcer.exceptions import RuleViolation
from sql_enforcer.parser import SQLParser
from sql_enforcer.rules import NoCreateAppRoleRule


class TestNoCreateAppRoleRule:
    def test_check_method_1(self) -> None:
        rule = NoCreateAppRoleRule()
        statements = SQLParser.get_statements("CREATE APPLICATION ROLE test_app_role WITH PASSWORD = 'test_password';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoCreateAppRoleRule()
        statements = SQLParser.get_statements("EXEC sp_addapprole 'test_app_role', 'test_password';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_database_role(self) -> None:
        rule = NoCreateAppRoleRule()
        statements = SQLParser.get_statements("ALTER ROLE test_role ADD MEMBER test_user;")
        rule.check(statements)

    def test_server_role(self) -> None:
        rule = NoCreateAppRoleRule()
        statements = SQLParser.get_statements("CREATE SERVER ROLE test_role;")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoCreateAppRoleRule()
        statement = SQLParser.get_statements(
            "CREATE APPLICATION ROLE test_app_role \
                                             WITH PASSWORD = 'test_password';"
        )[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
