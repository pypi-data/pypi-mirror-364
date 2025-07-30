"""Sage time formatting."""

from .conversions import seconds_to_hms


def time_as_clock(total_seconds: float, include_centiseconds=False) -> str:
    """
    Take a time in total seconds, convert it to the correct time units
    (hours, minutes, seconds) and format it into a 00:00:00 format.
    """
    hours, minutes, seconds = seconds_to_hms(total_seconds)

    if include_centiseconds:
        centiseconds = round((total_seconds % 1) * 100) % 100
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{centiseconds:02d}"

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def time_in_english(total_seconds: float) -> str:
    """
    Take a time in total seconds, convert it to the correct time units
    (hours, minutes, seconds) and format it into English with proper
    singular/plural.
    """
    hours, minutes, seconds = seconds_to_hms(total_seconds)

    def pluralize(value, unit):
        return f"{value} {unit}" + ("" if value == 1 else "s")

    parts = []
    if hours:
        parts.append(pluralize(hours, "hour"))
    if minutes:
        parts.append(pluralize(minutes, "minute"))
    if seconds:
        parts.append(pluralize(seconds, "second"))

    return " ".join(parts) if parts else "0 seconds"
