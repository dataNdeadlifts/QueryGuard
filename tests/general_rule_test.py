from __future__ import annotations

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser
from queryguard.rules import NoCreateLogin, NoCreateServerRole


class TestGeneral:
    def test_check_multiple_violations(self) -> None:
        no_create_login_rule = NoCreateLogin()
        no_create_server_role_rule = NoCreateServerRole()
        statements = SQLParser.get_all_statements(
            "CREATE \n\
             LOGIN [test_login] WITH PASSWORD = 'test_password';\n\
             GO\nCREATE SERVER ROLE test_role;\nGO"
        )

        with pytest.raises(RuleViolation):
            no_create_login_rule.check(statements)

        with pytest.raises(RuleViolation):
            no_create_server_role_rule.check(statements)
