from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoAlterDatabaseAll


class TestNoAlterDatabaseFiles:
    def test_check_method_files_1(self) -> None:
        rule = NoAlterDatabaseAll()
        statements = SQLParser.get_all_statements("ALTER DATABASE test_database ADD FILEGROUP test_filegroup;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_files_2(self) -> None:
        rule = NoAlterDatabaseAll()
        statements = SQLParser.get_all_statements(
            "ALTER DATABASE test_database ADD LOG FILE \
                                              (NAME = test_file, FILENAME = 'test_file_path', \
                                              SIZE = 5MB, MAXSIZE = 100MB, FILEGROWTH = 5MB);"
        )
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_files_3(self) -> None:
        rule = NoAlterDatabaseAll()
        statements = SQLParser.get_all_statements("ALTER DATABASE test_database REMOVE FILE test_file;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_files_4(self) -> None:
        rule = NoAlterDatabaseAll()
        statements = SQLParser.get_all_statements(
            "ALTER DATABASE test_database MODIFY FILE \
                                              (NAME = test_file, SIZE = 200MB);"
        )
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_files_5(self) -> None:
        rule = NoAlterDatabaseAll()
        statements = SQLParser.get_all_statements("DBCC SHRINKFILE (test_file, 1);")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_files_6(self) -> None:
        rule = NoAlterDatabaseAll()
        statements = SQLParser.get_all_statements("DBCC SHRINKDATABASE (test_database, 10);")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_files_7(self) -> None:
        rule = NoAlterDatabaseAll()
        statements = SQLParser.get_all_statements("DBCC SHOWCONTIG ('test_database.test_table');")
        rule.check(statements)

    def test_check_method_files_8(self) -> None:
        rule = NoAlterDatabaseAll()
        statements = SQLParser.get_all_statements("ALTER DATABASE [test_database] SET READ_ONLY;")
        with pytest.raises(RuleViolation):
            rule.check(statements)
