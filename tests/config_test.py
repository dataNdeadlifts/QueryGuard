from __future__ import annotations

import os
from pathlib import Path
from typing import cast

import pytest

from queryguard import rules
from queryguard.config import BaseSetting, CLIHandler, Config, FileHandler, RequestParams, SelectSetting
from queryguard.exceptions import TerminatingError
from queryguard.output import ConsoleText


class TestConfig:
    def test_config_default(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        # set cli arguments
        request_params = cast(
            RequestParams,
            {
                "path": "",
                "settings": "",
                "select": "",
                "ignore": "",
                "debug": False,
            },
        )
        config = Config(request_params)

        assert config.handlers["file"].__repr__() == "FileHandler()"
        assert config.get_setting("select") == ["S"]
        assert config.get_setting("ignore") == [""]
        assert config.all_rule_ids == [x.id for x in rules.BaseRule.__subclasses__()]  # type: ignore[comparison-overlap]
        assert config.get_setting("debug") is False
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
        request_params = cast(
            RequestParams,
            {
                "path": "",
                "settings": tmp_path / "queryguard.toml",
                "select": "",
                "ignore": "",
                "debug": False,
            },
        )
        config = Config(request_params)

        assert config.get_setting("select") == ["S001", "S002"]
        assert config.get_setting("ignore") == ["S001"]
        assert config.get_setting("debug") is True
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
        request_params = cast(
            RequestParams,
            {
                "path": "",
                "settings": "",
                "select": "",
                "ignore": "",
                "debug": False,
            },
        )
        config = Config(request_params)
        config_file.unlink()

        assert config.handlers["file"].file == Path("queryguard.toml").resolve()  # type: ignore[attr-defined]
        assert config.get_setting("select") == ["S001", "S002"]
        assert config.get_setting("ignore") == ["S001"]
        assert config.get_setting("debug") is True  #
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
        request_params = cast(
            RequestParams,
            {
                "path": "",
                "settings": tmp_path / "queryguard.toml",
                "select": "S001, S002",
                "ignore": "S001",
                "debug": "false",
            },
        )
        config = Config(request_params)

        assert config.get_setting("select") == ["S001", "S002"]
        assert config.get_setting("ignore") == ["S001"]
        assert config.get_setting("debug") is False
        assert config.enabled_rules == ["S002"]

    def test_unexpected_values(self, tmp_path: Path) -> None:
        # set cli arguments
        request_params = cast(
            RequestParams,
            {
                "path": "",
                "settings": tmp_path / "queryguard.toml",
                "ignore": "",
                "debug": "",
            },
        )

        handler = CLIHandler(request_params)

        class UnexpectedSetting(BaseSetting):
            name = "unexpected"
            default = "unexpected"
            type = "str"

        setting = UnexpectedSetting()

        with pytest.raises(ValueError):
            handler.get(setting)

        with pytest.raises(ValueError):
            handler.convert_type(setting, 1)

    def test_unexpected_file(self, tmp_path: Path) -> None:
        config_file = tmp_path / "queryguard.toml"
        config_file.write_text("[tool.queryguard]\nselect = ['S001']\nignore = ['S001']\ndebug = true")
        handler = FileHandler(file_path=str(config_file))
        config_file.unlink()

        select = SelectSetting()
        assert handler.get(select) == ["S001"]

    def test_string_to_path(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        # create a temporary config file
        config_file = tmp_path / "queryguard.toml"
        config_file.write_text("")

        # set cli arguments
        request_params = cast(
            RequestParams,
            {
                "path": str(tmp_path),
                "settings": tmp_path / "queryguard.toml",
                "select": "S001, S002",
                "ignore": "S001",
                "debug": "false",
            },
        )
        config = Config(request_params)

        assert config.get_setting("path") == tmp_path

    def test_same_type(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        # create a temporary config file
        config_file = tmp_path / "queryguard.toml"
        config_file.write_text("")

        # set cli arguments
        request_params = cast(
            RequestParams,
            {
                "path": str(tmp_path),
                "settings": tmp_path / "queryguard.toml",
                "select": "S001, S002",
                "ignore": "S001",
                "debug": "false",
            },
        )
        config = Config(request_params)

        assert config.get_setting("path") == tmp_path

    def test_invalid_output_handler(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        # create a temporary config file
        config_file = tmp_path / "queryguard.toml"
        config_file.write_text("")

        # set cli arguments
        request_params = cast(
            RequestParams,
            {
                "path": str(tmp_path),
                "settings": tmp_path / "queryguard.toml",
                "select": "S001, S002",
                "ignore": "S001",
                "output": "invalid",
                "debug": "false",
            },
        )
        config = Config(request_params)

        with pytest.raises(TerminatingError):
            config.get_setting("output")

    def test_get_output_handler(self, tmp_path: Path) -> None:
        # set environment variables
        os.unsetenv("QUERYGUARD_SELECT")
        os.unsetenv("QUERYGUARD_IGNORE")
        os.unsetenv("QUERYGUARD_DEBUG")

        # create a temporary config file
        config_file = tmp_path / "queryguard.toml"
        config_file.write_text("")

        # set cli arguments
        request_params = cast(
            RequestParams,
            {
                "path": str(tmp_path),
                "settings": tmp_path / "queryguard.toml",
                "select": "S001, S002",
                "ignore": "S001",
                "output": "text",
                "debug": "false",
            },
        )
        config = Config(request_params)

        assert isinstance(config.get_setting("output"), ConsoleText)
