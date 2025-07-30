"""Sage create command."""

import click

from sage.config import presets


@click.command(short_help="Create a custom timer")
@click.argument("name", required=True)
@click.argument("duration", required=True)
def create(name, duration):
    """
    Create a custom timer with a memorable name. Duration accepts
    human-readable formats like "25m", "1h 30m", or "45 seconds".

    \b
    Examples:
        sage create pomodoro 25m
        sage create break "10 minutes"
        sage create titatnic 3hrs14min
    """
    try:
        presets.create(name, duration)
        click.echo(f"Successfully created timer '{name}'.")

    except ValueError as e:
        raise click.BadArgumentUsage(str(e))
