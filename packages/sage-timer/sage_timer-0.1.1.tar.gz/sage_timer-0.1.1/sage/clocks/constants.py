"""Sage constants."""

from enum import StrEnum


class DisplayText(StrEnum):
    """
    Stores all display text for use in the curses application window.
    """
    MISSING_SOUND = "Cannot find sound file. Timer will complete silently."
    RUNNING_HELP = "<q> Quit, <Space> Pause/Resume, <Enter> Increment counter"
    PAUSED = "Paused"
    TIMES_UP_HELP = "<q> Quit"
    TIMES_UP = "Time's up!"
    TIMES_UP_TIME = "00:00:00"
    TITLE = "sage"


class SoundFileName(StrEnum):
    """
    Stores sound filenames for use in the curses application.
    """
    TIMES_UP = "timesup.mp3"
