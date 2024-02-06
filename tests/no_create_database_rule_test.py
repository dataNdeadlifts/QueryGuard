from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoCreateDatabase


class TestNoCreateDatabase:
    def test_check_method_1(self) -> None:
        rule = NoCreateDatabase()
        statements = SQLParser.get_statements("CREATE DATABASE test_database;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoCreateDatabase()
        statements = SQLParser.get_statements("EXEC sp_attach_db 'test_database' 'test_database_file';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoCreateDatabase()
        statements = SQLParser.get_statements("EXEC sp_attach_single_file_db 'test_database' 'test_database_file';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoCreateDatabase()
        statements = SQLParser.get_statements("DBCC CLONEDATABASE (test_database, test_database_clone);")
        with pytest.raises(RuleViolation):
            rule.check(statements)
