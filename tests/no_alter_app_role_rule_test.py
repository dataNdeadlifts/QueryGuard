from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoAlterAppRole


class TestNoAlterAppRole:
    def test__str__(self) -> None:
        rule = NoAlterAppRole()
        assert rule.__str__() == "Rule: NoAlterAppRole (S012)"

    def test__repr__(self) -> None:
        rule = NoAlterAppRole()
        assert rule.__repr__() == "Rule: NoAlterAppRole (S012)"

    def test_check_method_1(self) -> None:
        rule = NoAlterAppRole()
        statements = SQLParser.get_statements("ALTER APPLICATION ROLE test_app_role WITH PASSWORD = 'test_password';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoAlterAppRole()
        statements = SQLParser.get_statements("EXEC sp_approlepassword 'test_app_role', 'test_password';  ")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_database_role(self) -> None:
        rule = NoAlterAppRole()
        statements = SQLParser.get_statements("ALTER ROLE test_role ADD MEMBER test_user;")
        rule.check(statements)

    def test_server_role(self) -> None:
        rule = NoAlterAppRole()
        statements = SQLParser.get_statements("ALTER SERVER ROLE test_role ADD MEMBER test_login;")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoAlterAppRole()
        statement = SQLParser.get_statements("ALTER APPLICATION ROLE test_app_role WITH PASSWORD = 'test_password';")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
