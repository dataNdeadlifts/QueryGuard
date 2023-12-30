from __future__ import annotations

import logging
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from queryguard import rules

logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """Base class for handling settings lookup."""

    _next_handler: None | BaseHandler = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def set_next(self, handler: BaseHandler) -> BaseHandler:
        """Sets the next handler in the chain.

        Args:
            handler (BaseHandler): The next handler in the chain.

        Returns:
            BaseHandler: The next handler.
        """
        self._next_handler = handler
        return handler

    @abstractmethod
    def get(self, setting: BaseSetting) -> bool | str | Iterable[None | str]:
        """Retrieves the value associated with the given key.

        Args:
            setting (BaseSetting): The key to retrieve the value for.

        Returns:
            None | str | list[str]: The value associated with the key, or None if not found.
        """
        if self._next_handler:
            return self._next_handler.get(setting)

        raise ValueError(f"Setting {setting.name} not found")

    def convert_type(
        self, setting: BaseSetting, value: bool | str | Iterable[str]
    ) -> bool | str | Iterable[None | str]:
        """Convert the type of the value."""
        if isinstance(value, str) and setting.type == "list":
            return [x.strip().upper() for x in value.split(",")]

        if isinstance(value, Iterable) and setting.type == "list":
            return [x.strip().upper() for x in value]

        if isinstance(value, str) and setting.type == "bool":
            if value.casefold() in ("true", "t", "yes", "y", "1"):
                return True

            return False

        if setting.type == "bool":
            return bool(value)

        raise ValueError(f"Invalid type {setting.type}")


class EnvironmentHandler(BaseHandler):
    """Abstract base class for handling environment settings."""

    prefix = "QUERYGUARD_"

    def get(self, setting: BaseSetting) -> bool | str | Iterable[None | str]:
        """Get the value of the specified setting.

        Args:
            setting (BaseSetting): The setting to retrieve.

        Returns:
            None | str | list[str]: The value of the setting.
        """
        value = os.environ.get("QUERYGUARD_" + setting.name.upper())

        if not value:
            value = os.environ.get("QUERYGUARD_" + setting.alias.upper())

        if value:
            return self.convert_type(setting, value)

        return super().get(setting)


class FileHandler(BaseHandler):
    """Abstract base class for handling file settings."""

    _config_file_paths: Iterable[Path] = (
        Path.cwd() / "queryguard.toml",
        Path.cwd() / ".queryguard.toml",
        Path.cwd() / ".config/queryguard.toml",
        Path.cwd() / ".config/.queryguard.toml",
        Path.cwd() / ".pyproject.toml",
        Path.cwd().parent / ".config/queryguard.toml",
        Path.cwd().parent / ".config/.queryguard.toml",
        Path.cwd().parent / ".pyproject.toml",
        Path.home() / "queryguard.toml",
        Path.home() / ".queryguard.toml",
        Path.home() / ".config/queryguard.toml",
        Path.home() / ".config/.queryguard.toml",
    )

    def __init__(self, file_path: None | str = None) -> None:
        """Initialize the Config object.

        Args:
            file_path (None | list[str], optional): The path to the config file. Defaults to None.
        """
        self.file: None | Path = Path(file_path) if file_path else None
        self._data: dict[str, Any] = {}
        self.file, self._data = self._get_config_file()
        self._data.setdefault("tool", {}).setdefault("queryguard", {})

    def _get_config_file(self) -> tuple[None | Path, dict[str, Any]]:
        if self.file:
            logger.debug(f"Loading configuration from {self.file}")
            with self.file.open(mode="rb") as f:
                return self.file, tomllib.load(f)

        for file in self._config_file_paths:
            if file.exists():
                logger.debug(f"Loading configuration from {file}")
                with file.open(mode="rb") as f:
                    return file, tomllib.load(f)

        return None, {}

    def get(self, setting: BaseSetting) -> bool | str | Iterable[None | str]:
        """Get the value of the specified setting.

        Args:
            setting (BaseSetting): The setting to retrieve.

        Returns:
            None | str | list[str]: The value of the setting.
        """
        value = self._data["tool"]["queryguard"].get(setting.name)

        if not value:
            value = self._data["tool"]["queryguard"].get(setting.alias)

        if value:
            return self.convert_type(setting, value)

        return super().get(setting)


class CLIHandler(BaseHandler):
    """Abstract base class for handling command line settings."""

    def __init__(self, cli_arguments: dict[str, Any]) -> None:
        """Initializes the Config object with the provided keyword arguments.

        Args:
            cli_arguments: A dictionary of key-value pairs representing the configuration options.

        Returns:
            None
        """
        for key, value in cli_arguments.items():
            setattr(self, key.casefold(), value)

    def get(self, setting: BaseSetting) -> bool | str | Iterable[None | str]:
        """Get the value of the specified setting.

        Args:
            setting (BaseSetting): The setting to retrieve.

        Returns:
            None | str | list[str]: The value of the setting.
        """
        value = getattr(self, setting.name.casefold(), None)

        if value:
            return self.convert_type(setting, value)

        return super().get(setting)


class DefaultHandler(BaseHandler):
    """Abstract base class for handling default settings."""

    def get(self, setting: BaseSetting) -> bool | str | Iterable[None | str]:
        """Get the value of the specified setting.

        Args:
            setting (BaseSetting): The setting to retrieve.

        Returns:
            None | str | list[str]: The value of the setting.
        """
        return self.convert_type(setting, setting.default)


@dataclass
class BaseSetting(ABC):
    """Base class for all settings."""

    def __init__(self) -> None:
        """Initialize a Setting object.

        Attributes:
            name: The name of the configuration value.
            default: The default value of the configuration value.
            environment_variable: The environment variable name.
            type: The type of the configuration value.
            source: The source of the configuration value.
        """
        self.environment_variable: str = self.name.upper()
        self.alias: str = ""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the configuration key."""

    @property
    @abstractmethod
    def default(self) -> bool | str | Iterable[str]:
        """Default value for the configuration."""

    @property
    @abstractmethod
    def type(self) -> Literal["str"] | Literal["list"] | Literal["bool"]:
        """Default value for the configuration."""


class SelectSetting(BaseSetting):
    """Select setting."""

    name = "select"
    alias = "enabled"
    default = "S"
    type = "list"


class IgnoreSetting(BaseSetting):
    """Ignore setting."""

    name = "ignore"
    alias = "disabled"
    default = ()
    type = "list"


class DebugSetting(BaseSetting):
    """Verbosity setting."""

    name = "debug"
    default = False
    type = "bool"


class Config:
    """The Config class manages the QueryGuard configuration.

    Attributes:
        enabled_rules: A list of enabled rule ids.
    """

    def __init__(self, cli_arguments: dict[str, Any]) -> None:
        """Initializes the configuration object."""
        self.handlers = {
            "cli": CLIHandler(cli_arguments),
            "environment": EnvironmentHandler(),
            "file": FileHandler(file_path=cli_arguments.get("settings", None)),
            "default": DefaultHandler(),
        }

        self.handlers["cli"].set_next(self.handlers["environment"]).set_next(self.handlers["file"]).set_next(
            self.handlers["default"]
        )

        settings = [x() for x in BaseSetting.__subclasses__()]  # type: ignore[abstract]

        for setting in settings:
            value = self.handlers["cli"].get(setting)
            logger.debug(f"Setting {setting.name} = {value}")
            setattr(self, setting.name, self.handlers["cli"].get(setting))

    @property
    def all_rule_ids(self) -> list[str]:
        """A list of all rule IDs."""
        return [x.id for x in rules.BaseRule.__subclasses__()]  # type: ignore[misc]

    @property
    def enabled_rules(self) -> list[str]:
        """List of enabled rule IDs."""
        return [
            id
            for id in self.all_rule_ids
            if any(id.startswith(enabled_id) for enabled_id in self.select)  # type: ignore[attr-defined]
            and not any(id.startswith(disabled_id) for disabled_id in self.ignore if disabled_id)  # type: ignore[attr-defined]
        ]
