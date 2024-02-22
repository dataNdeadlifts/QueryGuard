from __future__ import annotations

from typer.testing import CliRunner

from queryguard import __version__
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

    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--version"],
        )
        assert result.exit_code == 0
        assert result.output.strip() == __version__

    def test_missing_path(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli)
        assert result.exit_code == 2
        assert "Error: Missing argument 'path'" in result.output
