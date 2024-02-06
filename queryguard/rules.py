from __future__ import annotations

import logging
import re
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


class NoCreateLogin(BaseRule):
    """Checks for any SQL statements that create a login.

    ID: S001

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
            # using regex here to avoid false positive results for items like create user for login
            if re.match(r"^\s*(go|;)*\s*create\s+login", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_grantlogin"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addlogin"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addremotelogin"):
            self.handle_match(statement)


class NoDropLogin(BaseRule):
    """Checks for any SQL statements that drop a login.

    ID: S002

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
            if re.match(r"^\s*(go|;)*\s*drop\s+login", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_droplogin"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_dropremotelogin"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_revokelogin"):
            self.handle_match(statement)


class NoAlterLogin(BaseRule):
    """Checks for any SQL statements that alter a login.

    ID: S003

    This rule checks for the following statements:

    - ALTER LOGIN
    - sp_denylogin
    - sp_change_users_login
    - sp_password
    - sp_defaultdb
    - sp_defaultlanguage
    """

    rule = "NoAlterLogin"
    id = "S003"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if re.match(r"^\s*(go|;)*\s*alter\s+login", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_denylogin"):
            self.handle_match(statement)

        # TODO: Update to allow report functionality of sp_change_users_login
        for statement in SQLParser.get_procedure_calls(statements, "sp_change_users_login"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_password"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_defaultdb"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_defaultlanguage"):
            self.handle_match(statement)


class NoCreateServerRole(BaseRule):
    """Checks for any SQL statements that create a server role.

    ID: S004

    This rule checks for the following statements:

    - CREATE SERVER ROLE
    """

    rule = "NoCreateServerRole"
    id = "S004"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "create"):
            if re.match(r"^\s*(go|;)*\s*create\s+server\s+role", str(statement).casefold()):
                self.handle_match(statement)


class NoDropServerRole(BaseRule):
    """Checks for any SQL statements that drop a server role.

    ID: S005

    This rule checks for the following statements:

    - DROP SERVER ROLE
    """

    rule = "NoDropServerRole"
    id = "S005"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "drop"):
            if re.match(r"^\s*(go|;)*\s*drop\s+server\s+role", str(statement).casefold()):
                self.handle_match(statement)


class NoAlterServerRole(BaseRule):
    """Checks for any SQL statements that alter a server role.

    ID: S006

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
            if re.match(r"^\s*(go|;)*\s*alter\s+server\s+role", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addsrvrolemember"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_dropsrvrolemember"):
            self.handle_match(statement)


class NoCreateDatabaseRole(BaseRule):
    """Checks for any SQL statements that create a database role.

    ID: S007

    This rule checks for the following statements:

    - CREATE ROLE
    - sp_addrole
    """

    rule = "NoCreateDatabaseRole"
    id = "S007"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "create"):
            if re.match(r"^\s*(go|;)*\s*create\s+role", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addrole"):
            self.handle_match(statement)


class NoDropDatabaseRole(BaseRule):
    """Checks for any SQL statements that drop a database role.

    ID: S008

    This rule checks for the following statements:

    - DROP ROLE
    - sp_droprole
    """

    rule = "NoDropDatabaseRole"
    id = "S008"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "drop"):
            if re.match(r"^\s*(go|;)*\s*drop\s+role", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_droprole"):
            self.handle_match(statement)


class NoAlterDatabaseRole(BaseRule):
    """Checks for any SQL statements that alter a database role.

    ID: S009

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
            if re.match(r"^\s*(go|;)*\s*alter\s+role", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addrolemember"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_droprolemember"):
            self.handle_match(statement)


class NoCreateAppRole(BaseRule):
    """Checks for any SQL statements that create an application role.

    ID: S010

    This rule checks for the following statements:

    - CREATE APPLICATION ROLE
    - sp_addapprole
    """

    rule = "NoCreateAppRole"
    id = "S010"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "create"):
            if re.match(r"^\s*(go|;)*\s*create\s+application\s+role", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_addapprole"):
            self.handle_match(statement)


class NoDropAppRole(BaseRule):
    """Checks for any SQL statements that drop an application role.

    ID: S011

    This rule checks for the following statements:

    - DROP APPLICATION ROLE
    - sp_dropapprole
    """

    rule = "NoDropAppRole"
    id = "S011"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "drop"):
            if re.match(r"^\s*(go|;)*\s*drop\s+application\s+role", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_dropapprole"):
            self.handle_match(statement)


class NoAlterAppRole(BaseRule):
    """Checks for any SQL statements that alter an application role.

    ID: S012

    This rule checks for the following statements:

    - ALTER APPLICATION ROLE
    - sp_approlepassword
    """

    rule = "NoAlterAppRole"
    id = "S012"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if re.match(r"^\s*(go|;)*\s*alter\s+application\s+role", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_approlepassword"):
            self.handle_match(statement)


class NoDynamicSQL(BaseRule):
    """Checks for any SQL statements that use dynamic sql.

    ID: S013

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


class NoCreateUser(BaseRule):
    """Checks for any SQL statements that create a user.

    ID: S014

    This rule checks for the following statements:

    - CREATE USER
    - sp_adduser
    - sp_grantdbaccess
    """

    rule = "NoCreateUser"
    id = "S014"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "create"):
            if re.match(r"^\s*(go|;)*\s*create\s+user", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_adduser"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_grantdbaccess"):
            self.handle_match(statement)


class NoDropUser(BaseRule):
    """Checks for any SQL statements that drop a user.

    ID: S015

    This rule checks for the following statements:

    - DROP USER
    - sp_dropuser
    - sp_revokedbaccess
    """

    rule = "NoDropLogin"
    id = "S015"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "drop"):
            if re.match(r"^\s*(go|;)*\s*drop\s+user", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_dropuser"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_revokedbaccess"):
            self.handle_match(statement)


class NoAlterUser(BaseRule):
    """Checks for any SQL statements that alter a user.

    ID: S016

    This rule checks for the following statements:

    - ALTER USER
    - sp_change_users_login
    - sp_migrate_user_to_contained
    """

    rule = "NoAlterUser"
    id = "S016"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if re.match(r"^\s*(go|;)*\s*alter\s+user", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_change_users_login"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_migrate_user_to_contained"):
            self.handle_match(statement)


class NoCreateDatabase(BaseRule):
    """Checks for any SQL statements that create a database.

    ID: S017

    This rule checks for the following statements:

    - CREATE DATABASE
    - sp_attach_db
    - sp_attach_single_file_db
    - DBCC CLONEDATABASE
    """

    rule = "NoCreateDatabase"
    id = "S017"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "create"):
            if re.match(r"^\s*(go|;)*\s*create\s+database", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_attach_db"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_attach_single_file_db"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "CLONEDATABASE"):
            if statement.is_group and statement.parent.tokens[0].match(
                None,
                SQLParser._to_case_insensitive_regex("dbcc"),
                regex=True,
            ):
                self.handle_match(statement)


class NoDropDatabase(BaseRule):
    """Checks for any SQL statements that drop a database.

    ID: S018

    This rule checks for the following statements:

    - DROP DATABASE
    - sp_detach_db
    - sp_dbremove
    """

    rule = "NoDropDatabase"
    id = "S018"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "drop"):
            if re.match(r"^\s*(go|;)*\s*drop\s+database", str(statement).casefold()):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_detach_db"):
            self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "sp_dbremove"):
            self.handle_match(statement)


class NoAlterDatabaseAll(BaseRule):
    """Checks for any SQL statements that alter any database configuration.

    ID: S019

    This rule checks for the following statements:

    - ALTER DATABASE
    - DBCC SHRINKDATABASE
    - DBCC SHRINKFILE
    """

    # TODO: Add more checks for dbcc or procedures that alter database configuration

    rule = "NoAlterDatabaseAll"
    id = "S019"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if re.match(
                r"^\s*(go|;)*\s*alter\s+database",
                str(statement).casefold(),
            ):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "SHRINKDATABASE"):
            if statement.is_group and statement.parent.tokens[0].match(
                None,
                SQLParser._to_case_insensitive_regex("dbcc"),
                regex=True,
            ):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "SHRINKFILE"):
            if statement.is_group and statement.parent.tokens[0].match(
                None,
                SQLParser._to_case_insensitive_regex("dbcc"),
                regex=True,
            ):
                self.handle_match(statement)


class NoAlterDatabaseFiles(BaseRule):
    """Checks for any SQL statements that alter a database file.

    ID: S020

    This rule checks for the following statements:

    - ALTER DATABASE ADD FILE
    - ALTER DATABASE ADD LOG FILE
    - ALTER DATABASE ADD FILEGROUP
    - ALTER DATABASE REMOVE FILE
    - ALTER DATABASE REMOVE LOG FILE
    - ALTER DATABASE REMOVE FILEGROUP
    - ALTER DATABASE MODIFY FILE
    - ALTER DATABASE MODIFY LOG FILE
    - ALTER DATABASE MODIFY FILEGROUP
    - DBCC SHRINKDATABASE
    - DBCC SHRINKFILE
    """

    rule = "NoAlterDatabase"
    id = "S020"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if re.match(
                r"^\s*(go|;)*\s*alter\s+database\s+\w+\s+(add|remove|modify)\s+(file|log file|filegroup)",
                str(statement).casefold(),
            ):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "SHRINKDATABASE"):
            if statement.is_group and statement.parent.tokens[0].match(
                None,
                SQLParser._to_case_insensitive_regex("dbcc"),
                regex=True,
            ):
                self.handle_match(statement)

        for statement in SQLParser.get_procedure_calls(statements, "SHRINKFILE"):
            if statement.is_group and statement.parent.tokens[0].match(
                None,
                SQLParser._to_case_insensitive_regex("dbcc"),
                regex=True,
            ):
                self.handle_match(statement)


# TODO: NoCreateDatabaseAudit, NoDropDatabaseAudit, NoAlterDatabaseAudit
# TODO: NoCreateServerAudit, NoDropServerAudit, NoAlterServerAudit


class NoAlterServerConfiguration(BaseRule):
    """Checks for any SQL statements that alter the server configuration.

    ID: S021

    This rule checks for the following statements:

    - ALTER SERVER CONFIGURATION
    """

    rule = "NoAlterServerConfiguration"
    id = "S021"

    def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
        super().check(statements)
        for statement in SQLParser.get_ddl_statements(statements, "alter"):
            if re.match(
                r"^\s*(go|;)*\s*alter\s+server\s+configuration",
                str(statement).casefold(),
            ):
                self.handle_match(statement)
