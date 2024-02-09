from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoDropUser


class TestNoDropUser:
    def test_check_method_1(self) -> None:
        rule = NoDropUser()
        statements = SQLParser.get_all_statements("DROP USER [test_user];")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoDropUser()
        statements = SQLParser.get_all_statements("DROP USER IF EXISTS [test_user];")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoDropUser()
        statements = SQLParser.get_all_statements("EXEC sp_dropuser 'test_user';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoDropUser()
        statements = SQLParser.get_all_statements("EXEC sp_revokedbaccess 'test_user';")
        with pytest.raises(RuleViolation):
            rule.check(statements)
