"""Sage base CLI command."""

import click

from sage.cli.create import create
from sage.cli.delete import delete
from sage.cli.list import list
from sage.cli.rename import rename
from sage.cli.stopwatch import stopwatch
from sage.cli.timer import timer
from sage.cli.update import update


@click.group()
@click.version_option(package_name="sage-timer")
def sage():
    pass

sage.add_command(create)
sage.add_command(delete)
sage.add_command(list)
sage.add_command(rename)
sage.add_command(stopwatch)
sage.add_command(timer)
sage.add_command(update)


if __name__ == "__main__":
    sage()
