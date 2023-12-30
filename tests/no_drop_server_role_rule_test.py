import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoDropServerRoleRule


class TestNoDropServerRoleRule:
    def test_check_method_1(self) -> None:
        rule = NoDropServerRoleRule()
        statements = SQLParser.get_statements("DROP SERVER ROLE test_role;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_database_role(self) -> None:
        rule = NoDropServerRoleRule()
        statements = SQLParser.get_statements("DROP ROLE test_role;")
        rule.check(statements)

    def test_app_role(self) -> None:
        rule = NoDropServerRoleRule()
        statements = SQLParser.get_statements("DROP APPLICATION ROLE test_app_role;")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoDropServerRoleRule()
        statement = SQLParser.get_statements("DROP SERVER ROLE test_role;")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
