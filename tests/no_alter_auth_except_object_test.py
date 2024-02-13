from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoAlterAuthExceptObject


class TestNoAlterAuthExceptObject:
    def test_check_method_1(self) -> None:
        rule = NoAlterAuthExceptObject()
        statements = SQLParser.get_all_statements("ALTER AUTHORIZATION ON database::testdb TO TestLogin;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoAlterAuthExceptObject()
        statements = SQLParser.get_all_statements(
            "ALTER AUTHORIZATION ON OBJECT::test_schema.test_database TO TestUser;"
        )
        rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoAlterAuthExceptObject()
        statements = SQLParser.get_all_statements("ALTER AUTHORIZATION ON test_schema.test_database TO TestUser;")
        rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoAlterAuthExceptObject()
        statements = SQLParser.get_all_statements("ALTER AUTHORIZATION ON SCHEMA::test_table TO TestUser;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_5(self) -> None:
        rule = NoAlterAuthExceptObject()
        statements = SQLParser.get_all_statements("ALTER AUTHORIZATION ON ENDPOINT::test_endpoint TO TestLogin;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_6(self) -> None:
        rule = NoAlterAuthExceptObject()
        statements = SQLParser.get_all_statements("ALTER AUTHORIZATION ON SCHEMA::test_table TO TestUser;")
        with pytest.raises(RuleViolation):
            rule.check(statements)
