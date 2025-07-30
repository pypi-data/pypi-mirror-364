"""Sage update command."""

import click

from sage.common.formatting import time_in_english
from sage.common.conversions import hms_to_seconds
from sage.config import presets


@click.command(short_help="Update a timer's duration")
@click.argument("name", required=True)
@click.argument("duration", required=True)
def update(name: str, duration: str) -> None:
    """
    Update the duration of an existing timer. Duration accepts
    human-readable formats like "25m", "1h 30m", or "45 seconds".

    \b
    Examples:
        sage update pomodoro 30m
        sage update rest "20 minutes"
        sage update potato 1hr5m
    """
    try:
        preset = presets.update(name, duration)
        total_seconds = hms_to_seconds(**preset)
        click.echo(f"Successfully updated timer '{name}' to {time_in_english(total_seconds)}.")

    except ValueError as e:
        raise click.BadArgumentUsage(str(e))
