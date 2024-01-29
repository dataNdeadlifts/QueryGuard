from __future__ import annotations

import logging
from pathlib import Path

import click

from queryguard.config import Config, RequestParams
from queryguard.files import File

logger = logging.getLogger(__name__)


class RulesEngine:
    """The RulesEngine class represents the engine that runs the rules on SQL files.

    Attributes:
        rules (list[type[rules.BaseRule]]): A list of subclasses of BaseRule.
    """

    def __init__(self, arguments: RequestParams) -> None:
        """Initializes the RulesEngine class.

        Args:
            config (Config): The configuration object.
            arguments (RequestParams): The input arguments from the calling process.
        """
        self.config = self.get_config(arguments)
        self.rules = self.config.rules
        self.output_handler = self.config.get_setting("output")

    def __repr__(self) -> str:
        return "RulesEngine()"

    def get_config(self, arguments: RequestParams) -> Config:
        """The configuration object."""
        return Config(arguments)

    def get_files(self, input_path: Path) -> list[File]:
        """Retrieves a list of File objects from the input path.

        Args:
            input_path (str): The path to the input file or directory.

        Returns:
            list[File]: A list of File objects.
        """
        logger.debug(f"Getting files from {input_path}")
        path = input_path
        files = []
        if path.is_file():
            files.append(File(path))
        elif path.is_dir():
            for file in path.glob("**/*.sql"):
                files.append(File(file))
        else:
            raise click.ClickException(f"Invalid path: {path}")

        return files

    def run(self) -> None:
        """Evaluates each file in the input path for adherance to the enabled rules.

        Args:
            arguments (dict[str, Any]): The input arguments from the calling process.

        Returns:
            None
        """
        files = self.get_files(self.config.get_setting("path"))
        for file in self.output_handler.track(files, description="Processing..."):
            file.evaluate(self.rules)

        self.output_handler.process_result(files)

        for file in files:
            if file.violations:
                self.output_handler.exit_violation_found()

        self.output_handler.exit_violation_not_found()
