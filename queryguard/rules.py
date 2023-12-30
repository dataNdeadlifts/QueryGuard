from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import NoReturn

import sqlparse

from queryguard.exceptions import RuleViolation
from queryguard.parser import SQLParser

logger = logging.getLogger(__name__)


class BaseRule(ABC):
    """Abstract base class for SQL query rules.

    Attributes:
        rule (str): The name of the rule.
    """

    def __str__(self) -> str:
        return "Rule: " + self.rule + " (" + self.id + ")"

    def __repr__(self) -> str:
        return "Rule: " + self.rule + " (" + self.id + ")"

    @property
    @abstractmethod
    def rule(self) -> str:
        """Rule name.

        Returns:
            str: Rule name.
        """

    @property
    @abstractmethod
    def id(self) -> str:
        """Rule id.

        Returns:
            str: Rule id.
        """

    @abstractmethod
    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        """Checks query against adherance to rule.

        Args:
            statements (tuple[sqlparse.sql.Statement]): Parsed SQL statements to evaluate.

        Returns:
            None

        Raises:
            RuleViolation: If query fails a rule evaluation.
        """
        logger.debug(f"Checking rule {self.rule}")

    def handle_match(self, statement: sqlparse.sql.Statement) -> NoReturn:
        """Raises a RuleViolation exception when a rule is violated.

        Args:
            statement (sqlparse.sql.Statement): The statement that violated the rule.

        Raises:
            RuleViolation: If query fails a rule evaluation.
        """
        logger.debug(f"Rule {self.rule} matched statement {statement}")
        raise RuleViolation(self.rule, self.id, statement)


class NoCreateLoginRule(BaseRule):
    """Checks for any SQL statements that create a login.

    This rule checks for the following statements:
    - CREATE LOGIN
    - sp_grantlogin
    - sp_addlogin
    - sp_addremotelogin
    """

    rule = "NoCreateLogin"
    id = "S001"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "create"):
            if SQLParser.acts_on_type(statement, "login"):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_grantlogin"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addlogin"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addremotelogin"):
            self.handle_match(statement)


class NoDropLoginRule(BaseRule):
    """Checks for any SQL statements that drop a login, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - DROP LOGIN
    - sp_droplogin
    - sp_dropremotelogin
    - sp_revokelogin
    """

    rule = "NoDropLogin"
    id = "S002"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "drop"):
            if SQLParser.acts_on_type(statement, "login"):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_droplogin"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_dropremotelogin"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_revokelogin"):
            self.handle_match(statement)


class NoAlterLoginRule(BaseRule):
    """Checks for any SQL statements that alter a login, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - ALTER LOGIN
    - sp_denylogin
    - sp_change_users_login
    - sp_password
    """

    rule = "NoAlterLogin"
    id = "S003"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if SQLParser.acts_on_type(statement, "login"):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_denylogin"):
            self.handle_match(statement)

        # TODO: Update to allow report functionality of sp_change_users_login
        for statement in SQLParser.get_procedure_calls(statements, "sp_change_users_login"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_password"):
            self.handle_match(statement)


class NoCreateServerRoleRule(BaseRule):
    """Checks for any SQL statements that create a server role, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - CREATE SERVER ROLE
    """

    rule = "NoCreateServerRole"
    id = "S004"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "create"):
            if SQLParser.acts_on_type(statement, "server") and SQLParser.acts_on_type(statement, "role"):
                self.handle_match(statement)


class NoDropServerRoleRule(BaseRule):
    """Checks for any SQL statements that drop a server role, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - DROP SERVER ROLE
    """

    rule = "NoDropServerRole"
    id = "S005"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "drop"):
            if SQLParser.acts_on_type(statement, "server") and SQLParser.acts_on_type(statement, "role"):
                self.handle_match(statement)


class NoAlterServerRoleRule(BaseRule):
    """Checks for any SQL statements that alter a server role, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - ALTER SERVER ROLE
    - sp_addsrvrolemember
    - sp_dropsrvrolemember
    """

    rule = "NoAlterServerRole"
    id = "S006"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if SQLParser.acts_on_type(statement, "server") and SQLParser.acts_on_type(statement, "role"):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addsrvrolemember"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_dropsrvrolemember"):
            self.handle_match(statement)


class NoCreateDatabaseRoleRule(BaseRule):
    """Checks for any SQL statements that create a database role, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - CREATE ROLE
    - sp_addrole
    """

    rule = "NoCreateDatabaseRole"
    id = "S007"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "create"):
            if (
                SQLParser.acts_on_type(statement, "role")
                and not SQLParser.acts_on_type(statement, "server")
                and not SQLParser.acts_on_type(statement, "application")
            ):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addrole"):
            self.handle_match(statement)


class NoDropDatabaseRoleRule(BaseRule):
    """Checks for any SQL statements that drop a database role, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - DROP ROLE
    - sp_droprole
    """

    rule = "NoDropDatabaseRole"
    id = "S008"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "drop"):
            if (
                SQLParser.acts_on_type(statement, "role")
                and not SQLParser.acts_on_type(statement, "server")
                and not SQLParser.acts_on_type(statement, "application")
            ):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_droprole"):
            self.handle_match(statement)


class NoAlterDatabaseRoleRule(BaseRule):
    """Checks for any SQL statements that alter a database role, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - ALTER ROLE
    - sp_addrolemember
    - sp_droprolemember
    """

    rule = "NoAlterDatabaseRole"
    id = "S009"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if (
                SQLParser.acts_on_type(statement, "role")
                and not SQLParser.acts_on_type(statement, "server")
                and not SQLParser.acts_on_type(statement, "application")
            ):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addrolemember"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_droprolemember"):
            self.handle_match(statement)


class NoCreateAppRoleRule(BaseRule):
    """Checks for any SQL statements that create an application role, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - CREATE APPLICATION ROLE
    - sp_addapprole
    """

    rule = "NoCreateAppRole"
    id = "S010"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "create"):
            if SQLParser.acts_on_type(statement, "role") and SQLParser.acts_on_type(statement, "application"):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addapprole"):
            self.handle_match(statement)


class NoDropAppRoleRule(BaseRule):
    """Checks for any SQL statements that drop an application role, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - DROP APPLICATION ROLE
    - sp_dropapprole
    """

    rule = "NoDropAppRole"
    id = "S011"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "drop"):
            if SQLParser.acts_on_type(statement, "role") and SQLParser.acts_on_type(statement, "application"):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_dropapprole"):
            self.handle_match(statement)


class NoAlterAppRoleRule(BaseRule):
    """Checks for any SQL statements that alter an application role, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - ALTER APPLICATION ROLE
    - sp_approlepassword
    """

    rule = "NoAlterAppRole"
    id = "S012"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if SQLParser.acts_on_type(statement, "role") and SQLParser.acts_on_type(statement, "application"):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_approlepassword"):
            self.handle_match(statement)


class NoDynamicSQLRule(BaseRule):
    """Checks for any SQL statements that use dynamic sql, and raises a RuleViolation exception if found.

    This rule checks for the following statements:
    - EXEC (string)
    - sp_executesql
    """

    rule = "NoDynamicSQL"
    id = "S013"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_exec_string(statements):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_executesql"):
            self.handle_match(statement)
