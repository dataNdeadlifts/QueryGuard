from __future__ import annotations

from typer.testing import CliRunner

from queryguard.cli import cli


class TestCLI:
    def test_invalid_syntax(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--this-is-an-invalid-option",
            ],
        )
        assert result.exit_code == 2
        assert "Usage:" in result.output

    def test_success(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "./tests/sql/no_violations.sql",
            ],
        )
        assert result.exit_code == 0
        assert "Passed ✅" in result.output

    def test_failed(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "./tests/sql/multiple_violations.sql",
            ],
        )
        assert result.exit_code == 1
        assert "Failed ❌" in result.output

    def test_select(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "./tests/sql/alter_app_role_1.sql",
                "--select",
                "S013",
            ],
        )
        assert result.exit_code == 0

    def test_ignore(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "./tests/sql/alter_app_role_1.sql",
                "--ignore",
                "S012",
            ],
        )
        assert result.exit_code == 0

    def test_debug(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "./tests/sql/no_violations.sql",
                "--debug",
            ],
        )
        assert result.exit_code == 0
        assert "DEBUG:" in result.output
