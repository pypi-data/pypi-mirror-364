"""Command parsing for REPL mode."""

import shlex
from dataclasses import dataclass
from typing import Any

import click

from .context import ReplContext


@dataclass
class ParsedCommand:
    """Represents a parsed REPL command."""

    command_path: list[str]
    arguments: list[str]
    options: dict[str, Any]
    context_args: dict[str, Any]
    raw_input: str


class ReplCommandParser:
    """Parses REPL commands and injects context."""

    def __init__(self, click_group: click.Group) -> None:
        self.click_group = click_group
        self.command_map = self._build_command_map()

    def parse(self, input_text: str, context: ReplContext) -> ParsedCommand:
        """Parse input text into a structured command."""
        input_text = input_text.strip()
        if not input_text:
            raise click.ClickException("Empty command")

        # Tokenize the input
        try:
            tokens = shlex.split(input_text)
        except ValueError as e:
            raise click.ClickException(f"Invalid command syntax: {e}") from e

        if not tokens:
            raise click.ClickException("Empty command")

        # Handle REPL-specific commands
        if self._is_repl_command(tokens[0]):
            return self._parse_repl_command(tokens, context, input_text)

        # Parse as CLI command
        return self._parse_cli_command(tokens, context, input_text)

    def _is_repl_command(self, command: str) -> bool:
        """Check if command is REPL-specific."""
        repl_commands = {
            "use",
            "back",
            "exit",
            "quit",
            "help",
            "context",
            "clear",
            "history",
            "set",
            "get",
            "alias",
        }
        return command.lower() in repl_commands

    def _parse_repl_command(
        self, tokens: list[str], context: ReplContext, raw_input: str
    ) -> ParsedCommand:
        """Parse REPL-specific commands."""
        command = tokens[0].lower()

        return ParsedCommand(
            command_path=[command],
            arguments=tokens[1:],
            options={},
            context_args=context.get_context_args(),
            raw_input=raw_input,
        )

    def _parse_cli_command(
        self, tokens: list[str], context: ReplContext, raw_input: str
    ) -> ParsedCommand:
        """Parse CLI commands with context injection."""
        # Find the command path
        command_path = []
        remaining_tokens = tokens[:]
        current_group = self.click_group

        while remaining_tokens and isinstance(current_group, click.Group):
            token = remaining_tokens[0]

            if token in current_group.commands:
                command_path.append(token)
                remaining_tokens.pop(0)
                current_group = current_group.commands[token]
            else:
                break

        if not command_path:
            raise click.ClickException(f"Unknown command: {tokens[0]}")

        # Parse arguments and options
        arguments = []
        options = {}

        i = 0
        while i < len(remaining_tokens):
            token = remaining_tokens[i]

            if token.startswith("--"):
                # Long option
                if "=" in token:
                    key, value = token[2:].split("=", 1)
                    options[key] = value
                else:
                    key = token[2:]
                    if i + 1 < len(remaining_tokens) and not remaining_tokens[i + 1].startswith(
                        "-"
                    ):
                        options[key] = remaining_tokens[i + 1]
                        i += 1
                    else:
                        options[key] = True
            elif token.startswith("-"):
                # Short option
                key = token[1:]
                if i + 1 < len(remaining_tokens) and not remaining_tokens[i + 1].startswith("-"):
                    options[key] = remaining_tokens[i + 1]
                    i += 1
                else:
                    options[key] = True
            else:
                # Argument
                arguments.append(token)

            i += 1

        return ParsedCommand(
            command_path=command_path,
            arguments=arguments,
            options=options,
            context_args=context.get_context_args(),
            raw_input=raw_input,
        )

    def _build_command_map(self) -> dict[str, click.Command]:
        """Build a map of all available commands."""
        command_map = {}

        def _add_commands(group: click.Group, path: list[str] | None = None) -> None:
            if path is None:
                path = []

            for name, command in group.commands.items():
                full_path = path + [name]
                command_map[" ".join(full_path)] = command

                if isinstance(command, click.Group):
                    _add_commands(command, full_path)

        _add_commands(self.click_group)
        return command_map
