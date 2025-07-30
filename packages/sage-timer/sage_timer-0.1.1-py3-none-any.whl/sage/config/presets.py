"""Sage preset configurations."""

import json
from pathlib import Path
from typing import TypeAlias

import click
from platformdirs import user_config_dir

from sage.common.conversions import time_input_to_hms, hms_to_seconds


PresetDict: TypeAlias = dict[str, int]
PresetsDict: TypeAlias = dict[str, PresetDict]


def get_json_file() -> Path:
    """
    Retrieve path to the JSON file storing presets.
    """
    try:
        config_dir = Path(user_config_dir("sage"))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "presets.json"

    except OSError as e:
        click.echo(f"Warning: Could not access config directory ({e}). Using home directory.", err=True)
        return Path.home() / ".sage_presets.json"


def create_defaults() -> PresetsDict:
    """
    Create and return default presets.
    """
    return {
        "johncage": {"hours": 0, "minutes": 4, "seconds": 33},
        "pomodoro": {"hours": 0, "minutes": 25, "seconds": 0},
        "potato": {"hours": 0, "minutes": 50, "seconds": 0},
        "break": {"hours": 0, "minutes": 10, "seconds": 0},
    }


def load_all() -> PresetsDict:
    """
    Load and return presets, creating defaults if the file doesn't exist.
    """
    presets_file = get_json_file()

    if not presets_file.exists():
        default_presets = create_defaults()
        save_all(default_presets)
        return default_presets

    try:
        with open(presets_file, "r") as f:
            return json.load(f)

    except Exception:
        return create_defaults()


def save_all(presets: PresetsDict) -> None:
    """
    Save presets to JSON file.
    """
    presets_file = get_json_file()

    try:
        with open(presets_file, "w") as f:
            json.dump(presets, f, indent=2)

    except Exception as e:
        raise click.ClickException(f"Could not save presets: {e}")


def get(name: str) -> PresetDict | None:
    """
    Get a specific preset by name.
    """
    presets = load_all()
    return presets.get(name)


def create(name: str, time_input: str) -> PresetDict:
    """
    Create a preset and save it.
    """
    if get(name):
        raise ValueError(f"'{name}' is already a preset.")

    hours, minutes, seconds = time_input_to_hms(time_input)
    total_seconds = hms_to_seconds(hours, minutes, seconds)

    if total_seconds <= 0:
        raise ValueError("Duration must be greater than 0 seconds.")

    if total_seconds > 86400:
        raise ValueError("Duration cannot exceed 24 hours.")

    presets = load_all()
    presets[name] = {
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds
    }

    save_all(presets)
    return presets[name]


def delete(name: str) -> None:
    """
    Delete a preset.
    """
    if get(name) is None:
        raise ValueError(f"'{name}' is not a preset.")

    presets = load_all()
    del presets[name]
    save_all(presets)


def rename(name: str, new_name: str) -> PresetDict:
    """
    Rename a preset.
    """
    if get(name) is None:
        raise ValueError(f"'{name}' is not a preset.")

    presets = load_all()
    presets.update({new_name: presets.pop(name)})

    save_all(presets)
    return presets[new_name]


def update(name: str, duration: str) -> PresetDict:
    """
    Update a preset's duration.
    """
    if get(name) is None:
        raise ValueError(f"'{name}' is not a preset.")

    hours, minutes, seconds = time_input_to_hms(duration)
    presets = load_all()
    presets[name] = {
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds
    }

    save_all(presets)
    return presets[name]
