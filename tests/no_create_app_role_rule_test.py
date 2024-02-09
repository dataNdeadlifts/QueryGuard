from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoCreateAppRole


class TestNoCreateAppRole:
    def test_check_method_1(self) -> None:
        rule = NoCreateAppRole()
        statements = SQLParser.get_all_statements(
            "CREATE APPLICATION ROLE test_app_role WITH PASSWORD = 'test_password';"
        )
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoCreateAppRole()
        statements = SQLParser.get_all_statements("EXEC sp_addapprole 'test_app_role', 'test_password';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_database_role(self) -> None:
        rule = NoCreateAppRole()
        statements = SQLParser.get_all_statements("ALTER ROLE test_role ADD MEMBER test_user;")
        rule.check(statements)

    def test_server_role(self) -> None:
        rule = NoCreateAppRole()
        statements = SQLParser.get_all_statements("CREATE SERVER ROLE test_role;")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoCreateAppRole()
        statement = SQLParser.get_all_statements(
            "CREATE APPLICATION ROLE test_app_role \
                                             WITH PASSWORD = 'test_password';"
        )[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
