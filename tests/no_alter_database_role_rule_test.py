from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoAlterDatabaseRole


class TestNoAlterDatabaseRole:
    def test_check_method_1(self) -> None:
        rule = NoAlterDatabaseRole()
        statements = SQLParser.get_statements("ALTER ROLE test_role ADD MEMBER test_user; ")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoAlterDatabaseRole()
        statements = SQLParser.get_statements("EXEC sp_addrolemember 'test_role', 'test_user'; ")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoAlterDatabaseRole()
        statements = SQLParser.get_statements("EXEC sp_droprolemember 'test_role', 'test_user';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_server_role(self) -> None:
        rule = NoAlterDatabaseRole()
        statements = SQLParser.get_statements("ALTER SERVER ROLE test_role ADD MEMBER test_user;")
        rule.check(statements)

    def test_app_role(self) -> None:
        rule = NoAlterDatabaseRole()
        statements = SQLParser.get_statements("ALTER APPLICATION ROLE test_app_role WITH PASSWORD = 'test_password';")
        rule.check(statements)

    def test_handle_match_method(self) -> None:
        rule = NoAlterDatabaseRole()
        statement = SQLParser.get_statements("ALTER ROLE test_role ADD MEMBER test_user; ")[0]
        with pytest.raises(RuleViolation):
            rule.handle_match(statement)
