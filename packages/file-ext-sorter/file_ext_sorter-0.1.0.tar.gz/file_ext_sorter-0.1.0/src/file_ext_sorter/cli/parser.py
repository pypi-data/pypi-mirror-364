"""
Custom argument parser with enhanced help output.

Provides colored usage, subtitles, and optional epilog support
for a better CLI user experience.
"""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

import argparse
import platform
from typing import List, Optional, NoReturn

from colorama import Style, Fore


class CustomArgumentParser(argparse.ArgumentParser):
    """ArgumentParser subclass providing enhanced, colored help output."""

    def __init__(
        self,
        *args,
        app_title: Optional[str] = None,
        subtitle: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the custom argument parser.

        Args:
            app_title (str, optional): Title of the CLI application.
            subtitle (str, optional): Subtitle displayed below the title.
        """
        self.app_title = app_title
        self.subtitle = subtitle
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> NoReturn:
        """
        Override default error handler to provide colored and styled output.

        Args:
            message (str): The error message to display.

        Raises:
            SystemExit: Always exits with status code 2.
        """
        self.exit(
            2,
            f"{Fore.RED}❌ Error: {message}{Style.RESET_ALL}\n\n"
            f"{self.format_usage()}\n\n"
            f"{Fore.YELLOW}💡 Tip: Use --help to see usage instructions.{Style.RESET_ALL}\n",
        )

    def format_help(self) -> str:
        """
        Generate a customized help message with title, subtitle,
        usage, options, and epilog.

        Returns:
            str: The full help message.
        """
        help_parts: List[str] = []

        if self.app_title:
            help_parts.append(
                f"\n{Style.BRIGHT}{self.app_title.upper()}{Style.RESET_ALL}\n"
            )

        if self.subtitle:
            help_parts.append(self.subtitle)
            help_parts.append("")  # blank line

        if self.description:
            help_parts.append(f"{self.description}")
            help_parts.append("")  # blank line

        help_parts.extend(
            [
                self.format_usage(),
                "",  # blank line
                self.format_positionals(),
                self.format_optionals(),
            ]
        )

        if self.epilog:
            help_parts.append(f"{Style.DIM}{self.epilog}{Style.RESET_ALL}")
            help_parts.append("")  # Ensure newline at the end

        return "\n".join(help_parts)

    def format_usage(self):
        """
        Generate a platform-specific usage and example command.

        Returns:
            str: Usage and example command string.
        """
        is_windows = platform.system() == "Windows"

        usage_cmd = (
            f"{self.prog} <source> <output>"
            if is_windows
            else f"{self.prog} <source> <output>"
        )
        example_cmd = (
            f"{self.prog} path\\to\\source\\folder path\\to\\output\\folder"
            if is_windows
            else f"{self.prog} ./path/to/source/folder ./path/to/output/folder"
        )
        return "\n".join(
            [
                f"Usage:    {usage_cmd}",
                f"Example:  {example_cmd}",
            ]
        )

    def format_positionals(self) -> str:
        """
        Format and return help section for positional arguments.

        Returns:
            str: Formatted positional argument help section.
        """
        return self._format_actions(
            self._get_positional_actions(), title="Positional arguments"
        )

    def format_optionals(self) -> str:
        """
        Format and return help section for optional arguments.

        Returns:
            str: Formatted optional argument help section.
        """
        return self._format_actions(self._get_optional_actions(), title="Options")

    def _format_actions(self, actions, title) -> str:
        """
        Format a given list of argparse actions with a section title.

        Args:
            actions (list): List of argparse actions.
            title (str): Section title for these actions.

        Returns:
            str: Formatted help section.
        """
        if not actions:
            return ""
        formatter = self._get_formatter()
        formatter.start_section(title)
        formatter.add_arguments(actions)
        formatter.end_section()
        return formatter.format_help()
