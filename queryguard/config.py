from __future__ import annotations

import logging
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal, TypedDict

from rich.console import Console

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # pragma: no cover

from queryguard import output, rules

logger = logging.getLogger(__name__)


class RequestParams(TypedDict):
    """Request input parameters."""

    path: Path
    settings: str
    select: str
    ignore: str
    debug: bool


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
    def get(self, setting: BaseSetting) -> bool | str | Iterable[None | str] | Path:
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
        self,
        setting: BaseSetting,
        value: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Convert the type of the value."""
        # handle lists
        if isinstance(value, str) and setting.type == "list":
            return [x.strip().upper() for x in value.split(",")]

        if isinstance(value, Iterable) and setting.type == "list":
            return [x.strip().upper() for x in value]

        # handle bools
        if isinstance(value, str) and setting.type == "bool":
            if value.casefold() in ("true", "t", "yes", "y", "1"):
                return True

            return False

        if setting.type == "bool":
            return bool(value)

        # handle paths
        if isinstance(value, Path) and setting.type == "path":
            return value

        if isinstance(value, str) and setting.type == "path":
            return Path(value)

        # handle generics
        if type(value).__name__.casefold() == setting.type.casefold():
            return value  # pragma: no cover

        raise ValueError(f"Can't convert type {type(value).__name__} to {setting.type}.")


class EnvironmentHandler(BaseHandler):
    """Abstract base class for handling environment settings."""

    prefix = "QUERYGUARD_"

    def get(self, setting: BaseSetting) -> Any:  # noqa: ANN401
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

    def get(self, setting: BaseSetting) -> Any:  # noqa: ANN401
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

    def __init__(self, cli_arguments: RequestParams) -> None:
        """Initializes the Config object with the provided keyword arguments.

        Args:
            cli_arguments: A dictionary of key-value pairs representing the configuration options.

        Returns:
            None
        """
        for key, value in cli_arguments.items():
            setattr(self, key.casefold(), value)

    def get(self, setting: BaseSetting) -> Any:  # noqa: ANN401
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

    def get(self, setting: BaseSetting) -> Any:  # noqa: ANN401
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
    def default(self) -> bool | str | Iterable[str] | Path | None:
        """Default value for the configuration."""

    @property
    @abstractmethod
    def type(self) -> Literal["str"] | Literal["list"] | Literal["bool"] | Literal["path"]:
        """Default value for the configuration."""

    def post_hook(self, value: Any) -> Any:  # noqa: ANN401
        """Post hook for setting value."""
        return value


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
    default = ""
    type = "list"


class DebugSetting(BaseSetting):
    """Verbosity setting."""

    name = "debug"
    default = False
    type = "bool"


class PathSetting(BaseSetting):
    """Path setting."""

    name = "path"
    default = None
    type = "path"


class OutputSetting(BaseSetting):
    """Path setting."""

    name = "output"
    default = "text"
    type = "str"

    def post_hook(self, value: str) -> output.BaseOutputHandler:
        """Post hook for converting id to output handler class instance."""
        try:
            return next(x() for x in output.BaseOutputHandler.__subclasses__() if x.id == value)  # type: ignore
        except StopIteration:
            Console().print(f"Invalid output handler: {value}", style="bold red")
            sys.exit(1)


class Config:
    """The Config class manages the QueryGuard configuration.

    Attributes:
        enabled_rules: A list of enabled rule ids.
    """

    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Config:  # noqa: ANN401
        """Creates a new Config object as a singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, arguments: RequestParams) -> None:
        """Initializes the configuration object."""
        self.arguments = arguments
        self.handlers = {
            "cli": CLIHandler(arguments),
            "environment": EnvironmentHandler(),
            "file": FileHandler(file_path=arguments.get("settings", None)),
            "default": DefaultHandler(),
        }

        self.handlers["cli"].set_next(self.handlers["environment"]).set_next(self.handlers["file"]).set_next(
            self.handlers["default"]
        )

        self.settings = {str(x.name): x() for x in BaseSetting.__subclasses__()}  # type: ignore[abstract]  # mypy doesn't understand that we are only initializing the concrete subclasses and not the abstract parent class

    def get_setting(self, name: str) -> Any:  # noqa: ANN401
        """Retrieves the value of the specified setting.

        Args:
            name (str): The setting to retrieve.

        Returns:
            Any: The value of the setting.
        """
        setting = self.settings[name]
        value = self.handlers["cli"].get(setting)
        logger.debug(f"Setting {setting.name} = {value}")
        post_hook_value = setting.post_hook(value)
        return post_hook_value

    @property
    def all_rule_ids(self) -> list[str]:
        """A list of all rule IDs."""
        return [str(x.id) for x in rules.BaseRule.__subclasses__()]

    @property
    def enabled_rules(self) -> list[str]:
        """List of enabled rule IDs."""
        return [
            id
            for id in self.all_rule_ids
            if any(id.startswith(enabled_id) for enabled_id in self.get_setting("select"))
            and not any(id.startswith(disabled_id) for disabled_id in self.get_setting("ignore") if disabled_id)
        ]

    @property
    def rules(self) -> list[type[rules.BaseRule]]:
        """A list of rules enabled in the configuration."""
        return [
            x  # type: ignore[type-abstract]
            for x in rules.BaseRule.__subclasses__()
            if x.id in self.enabled_rules  # type: ignore[comparison-overlap]
        ]
