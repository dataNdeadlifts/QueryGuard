from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoCreateDatabaseRole


class TestNoCreateDatabaseRole:
    def test_check_method_1(self) -> None:
        rule = NoCreateDatabaseRole()
        statements = SQLParser.get_all_statements("CREATE ROLE test_role;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoCreateDatabaseRole()
        statements = SQLParser.get_all_statements("EXEC sp_addrole 'test_role';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_server_role(self) -> None:
        rule = NoCreateDatabaseRole()
        statements = SQLParser.get_all_statements("CREATE SERVER ROLE test_role;")
        rule.check(statements)

    def test_app_role(self) -> None:
        rule = NoCreateDatabaseRole()
        statements = SQLParser.get_all_statements(
            "CREATE APPLICATION ROLE test_app_role WITH PASSWORD = 'test_password';"
        )
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoCreateDatabaseRole()
        statement = SQLParser.get_all_statements("CREATE ROLE test_role;")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
