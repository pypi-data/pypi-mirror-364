"""Command execution for REPL mode."""

from typing import Any

import click
from rich.console import Console
from rich.table import Table

from ..api_client import APIClient
from .context import ContextType, ReplContext
from .parser import ParsedCommand


class ReplCommandExecutor:
    """Executes commands in REPL mode."""

    def __init__(self, click_group: click.Group, click_ctx: click.Context) -> None:
        self.click_group = click_group
        self.click_ctx = click_ctx
        self.console = Console()

    def execute(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute a parsed command."""
        command_name = parsed_cmd.command_path[0]

        # Handle REPL-specific commands
        if command_name in ["use", "back", "exit", "quit", "help", "context", "clear"]:
            return self._execute_repl_command(parsed_cmd, context)

        # Execute CLI command
        return self._execute_cli_command(parsed_cmd, context)

    def _execute_repl_command(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute REPL-specific commands."""
        command = parsed_cmd.command_path[0]
        args = parsed_cmd.arguments

        if command == "use":
            return self._handle_use_command(args, context)
        elif command == "back":
            return self._handle_back_command(context)
        elif command in ["exit", "quit"]:
            return self._handle_exit_command()
        elif command == "help":
            return self._handle_help_command(args)
        elif command == "context":
            return self._handle_context_command(context)
        elif command == "clear":
            return self._handle_clear_command()
        else:
            raise click.ClickException(f"Unknown REPL command: {command}")

    def _execute_cli_command(self, parsed_cmd: ParsedCommand, context: ReplContext) -> Any:
        """Execute CLI commands with context injection."""
        # Resolve the command
        current_group: click.Command | click.Group = self.click_group
        for cmd_name in parsed_cmd.command_path:
            if isinstance(current_group, click.Group) and cmd_name in current_group.commands:
                current_group = current_group.commands[cmd_name]
            else:
                raise click.ClickException(
                    f"Command not found: {' '.join(parsed_cmd.command_path)}"
                )

        if not isinstance(current_group, click.Command):
            raise click.ClickException(f"Invalid command: {' '.join(parsed_cmd.command_path)}")

        # Build command line args list with context injection
        args = self._build_command_args(parsed_cmd, current_group)

        # Create a new context for command execution
        try:
            # Parse the args and invoke the command
            with current_group.make_context(
                info_name=" ".join(parsed_cmd.command_path),
                args=args,
                parent=self.click_ctx,
                allow_extra_args=True,
                allow_interspersed_args=False,
            ) as cmd_ctx:
                # Copy parent context object
                cmd_ctx.obj = self.click_ctx.obj
                # Invoke the command with the parsed context
                return current_group.invoke(cmd_ctx)
        except click.ClickException:
            raise
        except Exception as e:
            raise click.ClickException(f"Command execution failed: {e}") from e

    def _merge_parameters(
        self, parsed_cmd: ParsedCommand, command: click.Command
    ) -> dict[str, Any]:
        """Merge user parameters with context parameters."""
        merged = {}

        # Get parameter names for this command
        param_names = {param.name for param in command.params}

        # Add context arguments if they match command parameters
        for key, value in parsed_cmd.context_args.items():
            if key in param_names:
                merged[key] = value

        # Add user options (override context)
        for key, value in parsed_cmd.options.items():
            # Convert short options to long names if needed
            param_name = self._resolve_parameter_name(key, command)
            if param_name and param_name in param_names:
                merged[param_name] = value

        # Add positional arguments
        positional_params = [p for p in command.params if isinstance(p, click.Argument)]
        for i, arg_value in enumerate(parsed_cmd.arguments):
            if i < len(positional_params):
                param_name = positional_params[i].name
                merged[param_name] = arg_value

        return merged

    def _build_command_args(self, parsed_cmd: ParsedCommand, command: click.Command) -> list[str]:
        """Build command line arguments list with context injection."""
        args = []

        # Get parameter info
        param_map = {param.name: param for param in command.params}

        # Add context arguments as options if they match command parameters
        for key, value in parsed_cmd.context_args.items():
            if key in param_map:
                param = param_map[key]
                if isinstance(param, click.Option):
                    # Find the option flag to use
                    opt_flag = None
                    for opt in param.opts:
                        if opt.startswith("--"):
                            opt_flag = opt
                            break
                    if opt_flag:
                        args.extend([opt_flag, str(value)])

        # Add user-provided options (these override context)
        for key, value in parsed_cmd.options.items():
            # Add the option with proper formatting
            if len(key) == 1:
                args.append(f"-{key}")
            else:
                args.append(f"--{key}")
            if value is not True:  # Skip for boolean flags
                args.append(str(value))

        # Add positional arguments
        args.extend(parsed_cmd.arguments)

        return args

    def _resolve_parameter_name(self, key: str, command: click.Command) -> str | None:
        """Resolve short option names to full parameter names."""
        for param in command.params:
            if isinstance(param, click.Option) and (
                key in param.opts or f"-{key}" in param.opts or f"--{key}" in param.opts
            ):
                return param.name
        return key

    def _handle_use_command(self, args: list[str], context: ReplContext) -> str:
        """Handle 'use <type> [<name>]' command."""
        if len(args) < 1:
            return "Usage: use <client|site|gateway> [<name>]"

        context_type_str = args[0].lower()

        try:
            context_type = ContextType(context_type_str)
        except ValueError:
            return f"Invalid context type: {context_type_str}. Valid types: client, site, gateway"

        # If name provided, use it directly
        if len(args) >= 2:
            name = args[1]
            return self._switch_to_context(context_type, name, context)
        else:
            # No name provided - list available resources and let user choose
            return self._interactive_context_selection(context_type, context)

    def _handle_back_command(self, context: ReplContext) -> str:
        """Handle 'back' command to exit current context."""
        if context.exit_context():
            return "Exited context"
        else:
            return "Already at global context"

    def _handle_exit_command(self) -> str:
        """Handle 'exit' or 'quit' command."""
        raise EOFError("User requested exit")

    def _handle_help_command(self, args: list[str]) -> str:
        """Handle 'help' command."""
        if not args:
            return self._show_general_help()
        else:
            # TODO: Show help for specific command
            return f"Help for: {' '.join(args)}"

    def _handle_context_command(self, context: ReplContext) -> str:
        """Handle 'context' command to show current context."""
        if context.is_global:
            return "Current context: global"
        else:
            path = context.get_context_path()
            return f"Current context: {path}"

    def _handle_clear_command(self) -> str:
        """Handle 'clear' command to clear screen."""
        click.clear()
        return ""

    def _show_general_help(self) -> str:
        """Show general REPL help."""
        help_text = """
ACE IoT Models CLI - Interactive Mode

REPL Commands:
  help [command]         Show help for command or general help
  use <type> [<name>]    Switch to context (client, site, gateway)
                         Without name: list and select interactively
  back                   Exit current context
  context                Show current context
  clear                  Clear screen
  exit, quit             Exit REPL

Context Types:
  client [<name>]        Set client context
  site [<name>]          Set site context
  gateway [<name>]       Set gateway context

Examples:
  use site               # List sites and select interactively
  use site demo-site     # Enter site context directly
  points list            # List points for current site
  back                   # Exit site context

All regular CLI commands work in REPL mode with automatic context injection.
"""
        return help_text.strip()

    def _get_api_client(self) -> APIClient | None:
        """Get API client from context."""
        return self.click_ctx.obj.get("client")

    def _switch_to_context(self, context_type: ContextType, name: str, context: ReplContext) -> str:
        """Switch to a specific context after validation."""
        # Get API client
        api_client = self._get_api_client()
        if not api_client:
            return "Error: API client not configured. Please set ACEIOT_API_KEY."

        # Validate resource exists
        try:
            if context_type == ContextType.CLIENT:
                api_client.get_client(name)
            elif context_type == ContextType.SITE:
                api_client.get_site(name)
            elif context_type == ContextType.GATEWAY:
                # For gateways, we need to list and check
                gateways = api_client.get_gateways()
                gateway_names = [g.get("name", "") for g in gateways.get("items", [])]
                if name not in gateway_names:
                    raise ValueError(f"Gateway '{name}' not found")

            # If we get here, resource exists
            context.enter_context(context_type, name)
            return f"Switched to {context_type.value} context: {name}"

        except Exception as e:
            return f"Error: Could not switch to {context_type.value} '{name}': {e}"

    def _interactive_context_selection(
        self, context_type: ContextType, context: ReplContext
    ) -> str:
        """List resources and allow interactive selection."""
        # Get API client
        api_client = self._get_api_client()
        if not api_client:
            return "Error: API client not configured. Please set ACEIOT_API_KEY."

        try:
            # Get list of resources based on type
            if context_type == ContextType.CLIENT:
                result = api_client.get_clients(per_page=100)
                items = result.get("items", [])
                choices = [
                    (item.get("name", ""), item.get("nice_name", item.get("name", "")))
                    for item in items
                ]

            elif context_type == ContextType.SITE:
                # If in client context, filter by client
                params: dict[str, Any] = {"per_page": 100}
                if context.current_frame and context.current_frame.type == ContextType.CLIENT:
                    params["client_name"] = context.current_frame.name

                result = api_client.get_sites(**params)
                items = result.get("items", [])
                choices = [
                    (
                        item.get("name", ""),
                        f"{item.get('name', '')} ({item.get('client_name', '')})",
                    )
                    for item in items
                ]

            elif context_type == ContextType.GATEWAY:
                result = api_client.get_gateways(per_page=100)
                items = result.get("items", [])
                choices = [
                    (item.get("name", ""), f"{item.get('name', '')} ({item.get('site_name', '')})")
                    for item in items
                ]

            else:
                return f"Interactive selection not implemented for {context_type.value}"

            if not choices:
                return f"No {context_type.value}s found"

            # Show table of options
            table = Table(title=f"Available {context_type.value}s")
            table.add_column("#", style="cyan", width=4)
            table.add_column("Name", style="green")
            table.add_column("Description", style="yellow")

            for i, (name, desc) in enumerate(choices, 1):
                table.add_row(str(i), name, desc)

            self.console.print(table)

            # If only one choice, auto-select
            if len(choices) == 1:
                selected_name = choices[0][0]
                click.echo(
                    f"\nAuto-selecting the only available {context_type.value}: {selected_name}"
                )
            else:
                # Ask for selection by number
                click.echo(
                    f"\nEnter number (1-{len(choices)}) or press Ctrl+C to cancel: ", nl=False
                )
                try:
                    selection = click.prompt("", type=int, default=0, show_default=False)
                    if 1 <= selection <= len(choices):
                        selected_name = choices[selection - 1][0]
                    else:
                        return (
                            f"Invalid selection. Please enter a number between 1 and {len(choices)}"
                        )
                except (click.Abort, KeyboardInterrupt):
                    return "\nSelection cancelled"

            # Switch to selected context
            return self._switch_to_context(context_type, selected_name, context)

        except Exception as e:
            return f"Error listing {context_type.value}s: {e}"
