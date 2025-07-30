"""Sage time conversions."""

import re
from typing import TypeAlias


HoursMinutesSeconds: TypeAlias = tuple[int, int, int]


def hms_to_seconds(hours=0, minutes=0, seconds=0) -> int:
    """
    Converts hours, minutes, and seconds to total seconds.
    """
    return (hours * 3600) + (minutes * 60) + seconds


def seconds_to_hms(total_seconds: float) -> HoursMinutesSeconds:
    """
    Expand a time in seconds to hours, minutes, and seconds.
    """
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds - (hours * 3600)) // 60)
    seconds = int(total_seconds % 60)
    return (hours, minutes, seconds)


def time_input_to_seconds(time_input: str) -> int:
    """
    Convert a human-readable time string to total seconds.
    """

    def extract_time_value(pattern: str) -> int:
        match = re.search(pattern, time_input)
        return int(match.group(1)) if match else 0

    hours = extract_time_value(r"(\d+)\s*(h|hour|hours)")
    minutes = extract_time_value(r"(\d+)\s*(m|min|minute|minutes)")
    seconds = extract_time_value(r"(\d+)\s*(s|sec|second|seconds)")
    total = hours * 3600 + minutes * 60 + seconds

    return total


def time_input_to_hms(time_input: str) -> HoursMinutesSeconds:
    """
    Convert a human-readable time string to hours, minutes, and seconds.
    """
    return seconds_to_hms(
        time_input_to_seconds(time_input)
    )
