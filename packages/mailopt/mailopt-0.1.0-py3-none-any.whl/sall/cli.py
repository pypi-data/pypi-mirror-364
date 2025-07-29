"""
Main CLI entry point for sall.
"""

from typing import Dict, Any

import click

try:
    from importlib.metadata import entry_points as stdlib_entry_points
except ImportError:
    stdlib_entry_points = None  # type: ignore
try:
    from importlib_metadata import entry_points as backport_entry_points
except ImportError:
    backport_entry_points = None  # type: ignore


def _get_entry_points() -> Any:
    """Get entry points with fallback for different Python versions."""
    if stdlib_entry_points is not None:
        return stdlib_entry_points()
    elif backport_entry_points is not None:
        return backport_entry_points()
    else:
        raise ImportError("No entry_points implementation found")


def load_commands() -> Dict[str, click.Command]:
    """
    Load all registered commands from entry points.

    Returns:
        Dictionary mapping command names to Click command objects
    """
    commands = {}

    try:
        for entry_point in _get_entry_points().select(group="mailopt.commands"):
            try:
                command_func = entry_point.load()
                if hasattr(command_func, "name"):
                    commands[command_func.name] = command_func
                else:
                    # If no name attribute, use the entry point name
                    commands[entry_point.name] = command_func
            except Exception as e:
                click.echo(
                    f"Warning: Could not load command '{entry_point.name}': {e}",
                    err=True,
                )
    except Exception as e:
        click.echo(f"Warning: Could not load commands: {e}", err=True)

    return commands


@click.group()
@click.version_option(version="0.1.0", prog_name="mailopt")
def main() -> None:
    """
    MailOpt - CLI Python pour automatiser et optimiser les workflows email/front-end

    Outil incontournable pour automatiser le développement et l'optimisation d'emails.
    """
    pass


def create_cli() -> click.Group:
    """
    Create the CLI group with all registered commands.

    Returns:
        Click group with all commands loaded
    """
    # Load all commands
    commands = load_commands()

    # Add commands to the main group
    for name, command in commands.items():
        main.add_command(command, name=name)

    return main


# Create the CLI when module is imported
cli = create_cli()

if __name__ == "__main__":
    cli()
