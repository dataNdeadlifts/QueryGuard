from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoAlterUser


class TestNoAlterUser:
    def test_check_method_1(self) -> None:
        rule = NoAlterUser()
        statements = SQLParser.get_all_statements("ALTER USER [test_user] with name [other_name];")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoAlterUser()
        statements = SQLParser.get_all_statements("EXEC sp_change_users_login 'Update_One', 'test_login', 'test_user';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoAlterUser()
        statements = SQLParser.get_all_statements(
            "EXEC sp_migrate_user_to_contained \
                                              'test_user', 'keep_name', 'do_not_disable_login;"
        )
        with pytest.raises(RuleViolation):
            rule.check(statements)
