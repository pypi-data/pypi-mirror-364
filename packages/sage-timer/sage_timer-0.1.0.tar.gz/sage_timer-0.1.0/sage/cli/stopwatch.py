"""Sage stopwatch command."""

import click

from sage.clocks.stopwatch import Stopwatch


@click.command(short_help="Start a stopwatch")
@click.option("--paused", is_flag=True, help="Start stopwatch in a paused state.")
def stopwatch(**kwargs):
    """
    Start a stopwatch with centisecond precision.

    \b
    Example:
        sage stopwatch
    """
    stopwatch = Stopwatch()
    stopwatch.load(**kwargs)
