from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoAlterServerConfiguration


class TestNoAlterServerConfiguration:
    def test_check_method_1(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("ALTER SERVER CONFIGURATION SET BUFFER POOL EXTENSION OFF;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("ALTER SERVER ROLE server_role_name  ADD MEMBER login;")
        rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("sp_configure 'recovery interval', '3';")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("EXEC sp_configure 'clr enabled', 1;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_5(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("sp_configure")
        rule.check(statements)

    def test_check_method_6(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("sp_configure;")
        rule.check(statements)

    def test_check_method_7(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("sp_configure\ngo")
        rule.check(statements)

    def test_check_method_8(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("exec sp_configure;")
        rule.check(statements)

    def test_check_method_9(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("sp_configure @configname='hadoop connectivity';")
        rule.check(statements)

    def test_check_method_10(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_all_statements("execute sp_configure @configname = 'hadoop connectivity';")
        rule.check(statements)
