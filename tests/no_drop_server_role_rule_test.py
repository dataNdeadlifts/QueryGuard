from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoDropServerRole


class TestNoDropServerRole:
    def test_check_method_1(self) -> None:
        rule = NoDropServerRole()
        statements = SQLParser.get_all_statements("DROP SERVER ROLE test_role;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_database_role(self) -> None:
        rule = NoDropServerRole()
        statements = SQLParser.get_all_statements("DROP ROLE test_role;")
        rule.check(statements)

    def test_app_role(self) -> None:
        rule = NoDropServerRole()
        statements = SQLParser.get_all_statements("DROP APPLICATION ROLE test_app_role;")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoDropServerRole()
        statement = SQLParser.get_all_statements("DROP SERVER ROLE test_role;")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
