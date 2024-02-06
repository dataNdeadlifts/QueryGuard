from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoAlterServerConfiguration


class TestNoAlterServerConfiguration:
    def test_check_method_1(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_statements("ALTER SERVER CONFIGURATION SET BUFFER POOL EXTENSION OFF;")
        with pytest.raises(RuleViolation):
            rule.check(statements)

    def test_check_method_2(self) -> None:
        rule = NoAlterServerConfiguration()
        statements = SQLParser.get_statements("ALTER SERVER ROLE server_role_name  ADD MEMBER login;")
        rule.check(statements)
