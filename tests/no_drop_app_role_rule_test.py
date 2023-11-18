import pytest

from sql_enforcer.exceptions import RuleViolation
from sql_enforcer.parser import SQLParser
from sql_enforcer.rules import NoDropAppRoleRule


class TestNoDropAppRoleRule:
    def test_check_method_1(self) -> None:
        rule = NoDropAppRoleRule()
        statements = SQLParser.get_statements("DROP APPLICATION ROLE test_app_role;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoDropAppRoleRule()
        statements = SQLParser.get_statements("sp_dropapprole 'test_app_role';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_database_role(self) -> None:
        rule = NoDropAppRoleRule()
        statements = SQLParser.get_statements("DROP ROLE test_role;")
        rule.check(statements)

    def test_server_role(self) -> None:
        rule = NoDropAppRoleRule()
        statements = SQLParser.get_statements("DROP SERVER ROLE test_role;")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoDropAppRoleRule()
        statement = SQLParser.get_statements("DROP APPLICATION ROLE test_app_role;")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
