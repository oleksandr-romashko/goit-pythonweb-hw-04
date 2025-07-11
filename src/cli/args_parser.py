"""
Custom argument parser for the File Sorter CLI tool.

Provides formatted help output with colored usage, subtitles,
and optional epilog support.
"""

import argparse
import platform

from colorama import Style, Fore


class CustomArgumentParser(argparse.ArgumentParser):
    """Custom parser based on ArgumentParser with extra function for better CLI output"""

    def __init__(self, *args, app_title=None, subtitle=None, **kwargs):
        self.app_title = app_title
        self.subtitle = subtitle
        super().__init__(*args, **kwargs)

    def error(self, message):
        self.exit(
            2,
            f"{Fore.RED}❌ Error: {message}{Style.RESET_ALL}\n\n"
            f"{self.format_usage()}\n\n"
            f"{Fore.YELLOW}💡 Tip: Use --help to see usage instructions.{Style.RESET_ALL}\n",
        )

    def format_help(self):
        help_parts = []

        if self.app_title:
            help_parts.append(f"{Style.BRIGHT}{self.app_title}{Style.RESET_ALL}")

        if self.subtitle:
            help_parts.append(self.subtitle)
            help_parts.append("")  # blank line

        if self.description:
            help_parts.append(f"{Style.DIM}{self.description}{Style.RESET_ALL}")
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
            lines = (
                self.epilog
                if isinstance(self.epilog, list)
                else self.epilog.splitlines()
            )
            help_parts.extend(
                f"{Style.DIM}{Fore.GREEN}{line}{Style.RESET_ALL}" for line in lines
            )
            help_parts.append("")  # Ensure newline at end

        return "\n".join(help_parts)

    def format_usage(self):
        is_windows = platform.system() == "Windows"

        usage_cmd = (
            f"python {self.prog} <source> <target>"
            if is_windows
            else f"python3 ./{self.prog} <source> <target>"
        )
        example_cmd = (
            f"python {self.prog} downloads\\sources downloads\\sorted"
            if is_windows
            else f"python3 ./{self.prog} ./downloads/sources ./downloads/sorted"
        )
        return "\n".join(
            [
                f"Usage:    {usage_cmd}",
                f"Example:  {example_cmd}",
            ]
        )

    def format_positionals(self):
        return self._format_actions(
            self._get_positional_actions(), title="Positional arguments"
        )

    def format_optionals(self):
        return self._format_actions(self._get_optional_actions(), title="Options")

    def _format_actions(self, actions, title):
        if not actions:
            return ""
        formatter = self._get_formatter()
        formatter.start_section(title)
        formatter.add_arguments(actions)
        formatter.end_section()
        return formatter.format_help()
