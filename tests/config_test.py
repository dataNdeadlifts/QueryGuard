import os
from pathlib import Path

import pytest

from queryguard import rules
from queryguard.config import BaseSetting, CLIHandler, Config, FileHandler, SelectSetting


class TestConfig:
    def test_config_default(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        # set cli arguments
        cli_arguments = {
            "path": "",
            "settings": "",
            "select": "",
            "ignore": "",
            "debug": False,
        }
        config = Config(cli_arguments)

        assert config.handlers["file"].__repr__() == "FileHandler()"
        assert config.select == ["S"]  # type: ignore[attr-defined]
        assert config.ignore == []  # type: ignore[attr-defined]
        assert config.all_rule_ids == [x.id for x in rules.BaseRule.__subclasses__()]  # type: ignore[comparison-overlap]
        assert config.debug is False  # type: ignore[attr-defined]
        assert config.enabled_rules == [x.id for x in rules.BaseRule.__subclasses__()]  # type: ignore[comparison-overlap]

    def test_config_environment(self, tmp_path: Path) -> None:
        # set environment variables
        os.environ["QUERYGUARD_SELECT"] = "S001, S002"
        os.environ["QUERYGUARD_IGNORE"] = "S001"
        os.environ["QUERYGUARD_DEBUG"] = "true"

        # create a temporary config file
        config_file = tmp_path / "queryguard.toml"
        config_file.write_text("")

        # set cli arguments
        cli_arguments = {
            "path": "",
            "settings": tmp_path / "queryguard.toml",
            "select": "",
            "ignore": "",
            "debug": False,
        }
        config = Config(cli_arguments)

        assert config.select == ["S001", "S002"]  # type: ignore[attr-defined]
        assert config.ignore == ["S001"]  # type: ignore[attr-defined]
        assert config.debug is True  # type: ignore[attr-defined]
        assert config.enabled_rules == ["S002"]

    def test_config_file(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        # create a temporary config file
        config_file = Path("queryguard.toml")
        config_file.write_text("[tool.queryguard]\nselect = ['S001', 'S002']\nignore = ['S001']\ndebug = true")

        # set cli arguments
        cli_arguments = {
            "path": "",
            "settings": "",
            "select": "",
            "ignore": "",
            "debug": False,
        }
        config = Config(cli_arguments)
        config_file.unlink()

        assert config.handlers["file"].file == Path("queryguard.toml").resolve()  # type: ignore[attr-defined]
        assert config.select == ["S001", "S002"]  # type: ignore[attr-defined]
        assert config.ignore == ["S001"]  # type: ignore[attr-defined]
        assert config.debug is True  # type: ignore[attr-defined]
        assert config.enabled_rules == ["S002"]

    def test_config_cli(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        # create a temporary config file
        config_file = tmp_path / "queryguard.toml"
        config_file.write_text("")

        # set cli arguments
        cli_arguments = {
            "path": "",
            "settings": tmp_path / "queryguard.toml",
            "select": "S001, S002",
            "ignore": "S001",
            "debug": "false",
        }
        config = Config(cli_arguments)

        assert config.select == ["S001", "S002"]  # type: ignore[attr-defined]
        assert config.ignore == ["S001"]  # type: ignore[attr-defined]
        assert config.debug is False  # type: ignore[attr-defined]
        assert config.enabled_rules == ["S002"]

    def test_unexpected_values(self, tmp_path: Path) -> None:
        # set cli arguments
        cli_arguments = {
            "path": "",
            "settings": tmp_path / "queryguard.toml",
            "ignore": "",
            "debug": "",
        }

        handler = CLIHandler(cli_arguments)

        class UnexpectedSetting(BaseSetting):
            name = "unexpected"
            default = "unexpected"
            type = "str"

        setting = UnexpectedSetting()

        with pytest.raises(ValueError):
            handler.get(setting)

        with pytest.raises(ValueError):
            handler.convert_type(setting, 1)  # type: ignore[arg-type]

    def test_unexpected_file(self, tmp_path: Path) -> None:
        config_file = tmp_path / "queryguard.toml"
        config_file.write_text("[tool.queryguard]\nselect = ['S001']\nignore = ['S001']\ndebug = true")
        handler = FileHandler(file_path=str(config_file))
        config_file.unlink()

        select = SelectSetting()
        assert handler.get(select) == ["S001"]
