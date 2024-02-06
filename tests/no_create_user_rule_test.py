from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoCreateUser


class TestNoCreateUser:
    def test_check_method_1(self) -> None:
        rule = NoCreateUser()
        statements = SQLParser.get_statements("CREATE USER [test_user] FROM LOGIN [test_login];")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoCreateUser()
        statements = SQLParser.get_statements("EXEC sp_adduser 'test_login', 'test_user';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoCreateUser()
        statements = SQLParser.get_statements("EXEC sp_grantdbaccess 'test_login', 'test_user';")
        with pytest.raises(RuleViolation):
            rule.check(statements)
