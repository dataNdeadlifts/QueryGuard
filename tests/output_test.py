import json
from pathlib import Path

import pytest

from queryguard.exceptions import RuleViolation
from queryguard.files import File
from queryguard.output import ConsoleJson, ConsoleText
from queryguard.rules import NoCreateLogin


class TestConsoleText:
    def test_track(self, capsys: pytest.CaptureFixture) -> None:
        """Test the track function."""
        console_text = ConsoleText()
        iterable = [1, 2, 3]
        description = "Processing..."
        result = console_text.track(iterable, description)

        assert list(result) == iterable

    def test_process_result_passed(self, capsys: pytest.CaptureFixture) -> None:
        console_text = ConsoleText()
        files = [File(Path("file1.txt")), File(Path("file2.txt"))]
        console_text.process_result(files)
        captured = capsys.readouterr()

        assert "Passed ✅" not in captured.out
        assert "Failed ❌" in captured.out

    def test_process_result_failed(self, capsys: pytest.CaptureFixture) -> None:
        console_text = ConsoleText()
        files = [File(Path("file1.txt")), File(Path("file2.txt"))]
        files[0].status = "Failed ❌"
        files[0].violations = [
            RuleViolation(rule=NoCreateLogin.rule, id=NoCreateLogin.id, statement="SELECT * FROM table1"),
            RuleViolation(rule=NoCreateLogin.rule, id=NoCreateLogin.id, statement="SELECT * FROM table2"),
        ]
        files[1].status = "Passed ✅"

        console_text.process_result(files)
        captured = capsys.readouterr()

        assert "Failed ❌" in captured.out
        assert "Passed ✅" in captured.out
        assert NoCreateLogin.rule in captured.out
        assert "SELECT * FROM table1" in captured.out
        assert "SELECT * FROM table2" in captured.out


class TestConsoleJson:
    def test_track(self, capsys: pytest.CaptureFixture) -> None:
        """Test the track function."""
        console_text = ConsoleJson()
        iterable = [1, 2, 3]
        description = "Processing..."
        result = console_text.track(iterable, description)
        captured = capsys.readouterr()

        assert captured.out == ""
        assert list(result) == iterable

    def test_process_result_passed(self, capsys: pytest.CaptureFixture) -> None:
        console_text = ConsoleJson()
        files = [File(Path("file1.txt")), File(Path("file2.txt"))]
        console_text.process_result(files)
        captured = capsys.readouterr()

        assert (json_output := json.loads(captured.out))
        assert isinstance(json_output, list)
        assert json_output[0]["status"] == "Not Run"

    def test_process_result_failed(self, capsys: pytest.CaptureFixture) -> None:
        console_text = ConsoleJson()
        files = [File(Path("file1.txt")), File(Path("file2.txt"))]
        files[0].status = "Failed ❌"
        files[0].violations = [
            RuleViolation(rule=NoCreateLogin.rule, id=NoCreateLogin.id, statement="SELECT * FROM table1"),
            RuleViolation(rule=NoCreateLogin.rule, id=NoCreateLogin.id, statement="SELECT * FROM table2"),
        ]
        files[1].status = "Passed ✅"

        console_text.process_result(files)
        captured = capsys.readouterr()

        assert (json_output := json.loads(captured.out.strip().replace("\n", "")))
        assert isinstance(json_output, list)
        assert json_output[0]["status"] == "Failed"
        assert json_output[1]["status"] == "Passed"
