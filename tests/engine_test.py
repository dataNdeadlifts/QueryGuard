from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import cast

import pytest
import sqlparse
from click import ClickException

from queryguard.config import RequestParams
from queryguard.engine import RulesEngine
from queryguard.exceptions import RuleViolation, TerminatingError
from queryguard.files import File


@pytest.fixture  # type: ignore[misc]
def sample_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "test.sql"
    file_path.write_text("SELECT * FROM users;")
    return file_path


@pytest.fixture  # type: ignore[misc]
def sample_utf_16_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "test_utf_16.sql"
    file_path.write_text("SELECT * FROM users;", encoding="utf-16")
    return file_path


class TestEngine:
    def test_file_evaluate_no_violations(self, sample_file: Path) -> None:
        file = File(sample_file)
        file.evaluate([])
        assert file.status == "Passed ✅"
        assert len(file.violations) == 0
        assert file.__repr__() == f"File(path={sample_file!s}, status=Passed ✅)"

    def test_file_evaluate_no_violations_utf_16(self, sample_utf_16_file: Path) -> None:
        file = File(sample_utf_16_file)
        file.evaluate([])
        assert file.status == "Passed ✅"
        assert len(file.violations) == 0
        assert file.__repr__() == f"File(path={sample_utf_16_file!s}, status=Passed ✅)"

    def test_file_evaluate_with_violations(self, sample_file: Path) -> None:
        class TestRule:
            def check(self, statements: tuple[sqlparse.sql.Statement]) -> None:
                raise RuleViolation("RuleName", "RuleID", statements)

        file = File(sample_file)
        file.evaluate([TestRule])  # type: ignore[list-item]

        assert file.status == "Failed ❌"
        assert len(file.violations) == 1

    def test_rules_engine_get_files(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        file1 = test_dir / "file1.sql"
        file1.write_text("SELECT * FROM users;")
        file2 = test_dir / "file2.sql"
        file2.write_text("SELECT * FROM products;")
        file3 = test_dir / "file3.txt"
        file3.write_text("This is not an SQL file.")

        request_params = cast(
            RequestParams,
            {
                "path": test_dir,
                "settings": "",
                "select": "",
                "ignore": "",
                "debug": False,
            },
        )

        engine = RulesEngine(request_params)
        files = engine.get_files(test_dir)

        assert len(files) == 2
        assert all(isinstance(file, File) for file in files)
        assert all(file.path in [file1, file2] for file in files)
        assert engine.__repr__() == "RulesEngine()"

    def test_rules_engine_run(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        test_dir = tmp_path / "test_dir1"
        test_dir.mkdir()
        file1 = test_dir / "file1.sql"
        file1.write_text("SELECT * FROM users;")
        file2 = test_dir / "file2.sql"
        file2.write_text("SELECT * FROM products;")

        request_params = cast(
            RequestParams,
            {
                "path": test_dir,
                "settings": "",
                "select": "",
                "ignore": "",
                "debug": False,
            },
        )

        engine = RulesEngine(request_params)

        assert len(engine.get_files(file1)) == 1
        assert len(engine.get_files(test_dir)) == 2
        assert all(file.status == "Not Run" for file in engine.get_files(test_dir))

        shutil.rmtree(test_dir)
        with pytest.raises(ClickException):
            engine.run()

    def test_rules_engine_run_rule_violation(self, tmp_path: Path) -> None:
        # unset environment variables
        os.environ["QUERYGUARD_SELECT"] = ""
        os.environ["QUERYGUARD_IGNORE"] = ""
        os.environ["QUERYGUARD_DEBUG"] = ""

        # remove any existing config file
        config_file = tmp_path / "queryguard.toml"
        config_file.unlink(missing_ok=True)

        test_dir = tmp_path / "test_dir2"
        test_dir.mkdir()
        file1 = test_dir / "file1.sql"
        file1.write_text("CREATE LOGIN test WITH PASSWORD = 'test';")

        request_params = cast(
            RequestParams,
            {
                "path": file1,
                "settings": "",
                "select": "S",
                "ignore": "",
                "debug": False,
            },
        )
        engine = RulesEngine(request_params)

        with pytest.raises(TerminatingError) as e:
            engine.run()

        assert e.value.exit_code == 1
