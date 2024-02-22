from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoGrantExceptObject


class TestNoGrantExceptObject:
    def test_check_method_1(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant administer bulk operations to test_login")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant execute on DATABASE::test_database to test_user")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_3(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant select to test_user")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_4(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant select on test_table to test_user")
        rule.check(statements)

    def test_check_method_5(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant select on test_database.dbo.test_table to test_user")
        rule.check(statements)

    def test_check_method_6(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant select on OBJECT::dbo.test_table to test_user")
        rule.check(statements)

    def test_check_method_7(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements(
            "grant references (test_column) on OBJECT::dbo.test_table to test_user"
        )
        rule.check(statements)

    def test_check_method_8(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant unmask on OBJECT::dbo.test_table (test_column) to test_user")
        rule.check(statements)

    def test_check_method_9(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant select on SCHEMA::test_schema to test_user")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_10(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant alter on test_table to test_user")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_11(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant control on test_table to test_user")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_12(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant control on test_table to test_user")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_13(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant delete on test_table to test_user")
        rule.check(statements)

    def test_check_method_14(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant insert on test_table to test_user")
        rule.check(statements)

    def test_check_method_15(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant update on test_table to test_user")
        rule.check(statements)

    def test_check_method_16(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant execute on test_procedure to test_user")
        rule.check(statements)

    def test_check_method_17(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant execute on test_procedure to test_user")
        rule.check(statements)

    def test_check_method_18(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant receive on test_queue to test_user")
        rule.check(statements)

    def test_check_method_19(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant take ownership on test_table to test_user")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_20(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant view change tracking on test_table to test_user")
        rule.check(statements)

    def test_check_method_21(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant view definition on test_table to test_user")
        rule.check(statements)

    def test_check_method_22(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant select /* example comment */ on test_table to test_user")
        rule.check(statements)

    def test_check_method_23(self) -> None:
        rule = NoGrantExceptObject()
        statements = SQLParser.get_all_statements("grant")
        rule.check(statements)
