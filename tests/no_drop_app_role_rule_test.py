from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoDropAppRole


class TestNoDropAppRole:
    def test_check_method_1(self) -> None:
        rule = NoDropAppRole()
        statements = SQLParser.get_all_statements("DROP APPLICATION ROLE test_app_role;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoDropAppRole()
        statements = SQLParser.get_all_statements("sp_dropapprole 'test_app_role';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_database_role(self) -> None:
        rule = NoDropAppRole()
        statements = SQLParser.get_all_statements("DROP ROLE test_role;")
        rule.check(statements)

    def test_server_role(self) -> None:
        rule = NoDropAppRole()
        statements = SQLParser.get_all_statements("DROP SERVER ROLE test_role;")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoDropAppRole()
        statement = SQLParser.get_all_statements("DROP APPLICATION ROLE test_app_role;")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
