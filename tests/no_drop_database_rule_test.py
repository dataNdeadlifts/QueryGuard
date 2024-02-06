from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoDropDatabase


class TestNoDropDatabase:
    def test_check_method_1(self) -> None:
        rule = NoDropDatabase()
        statements = SQLParser.get_statements("DROP DATABASE test_database;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoDropDatabase()
        statements = SQLParser.get_statements("EXEC sp_detach_db 'test_database';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoDropDatabase()
        statements = SQLParser.get_statements("EXEC sp_dbremove 'test_database';")
        with pytest.raises(RuleViolation):
            rule.check(statements)
