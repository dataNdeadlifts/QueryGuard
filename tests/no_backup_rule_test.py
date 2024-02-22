from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoBackup


class TestNoBackup:
    def test_check_method_1(self) -> None:
        rule = NoBackup()
        statements = SQLParser.get_all_statements(
            "BACKUP DATABASE test_database TO DISK = 'Z:\test_folder\test_file.bak'"
        )
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoBackup()
        statements = SQLParser.get_all_statements("/*this is a test comment*/ backup log test_database TO test_device;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoBackup()
        statements = SQLParser.get_all_statements("EXEC backup;")
        rule.check(statements)
