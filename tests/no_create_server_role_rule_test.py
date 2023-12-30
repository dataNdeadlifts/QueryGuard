import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoCreateServerRoleRule


class TestNoCreateServerRoleRule:
    def test_check_method_1(self) -> None:
        rule = NoCreateServerRoleRule()
        statements = SQLParser.get_statements("CREATE SERVER ROLE test_role;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_database_role(self) -> None:
        rule = NoCreateServerRoleRule()
        statements = SQLParser.get_statements("CREATE ROLE test_role;")
        rule.check(statements)

    def test_app_role(self) -> None:
        rule = NoCreateServerRoleRule()
        statements = SQLParser.get_statements("CREATE APPLICATION ROLE test_app_role WITH PASSWORD = 'test_password';")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoCreateServerRoleRule()
        statement = SQLParser.get_statements("CREATE SERVER ROLE test_role;")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
