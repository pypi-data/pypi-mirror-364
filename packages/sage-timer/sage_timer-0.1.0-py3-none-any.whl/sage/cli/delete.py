"""Sage delete command."""

import click

from sage.config import presets


@click.command(short_help="Delete a timer")
@click.argument("name", required=True)
def delete(name):
    """
    Delete a saved timer. This action cannot be undone.

    \b
    Example:
        sage delete pomodoro
    """
    try:
        presets.delete(name)
        click.echo(f"Successfully deleted timer '{name}'.")

    except ValueError as e:
        raise click.BadArgumentUsage(str(e))
