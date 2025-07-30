"""Sage sound configurations."""

from pathlib import Path

from nava import play
from nava.errors import NavaBaseError


def get_file(filename: str) -> Path:
    """
    Get path to the given sound file.
    """
    project_root = Path(__file__).parent.parent.parent
    return Path(project_root, "sounds", filename).resolve()


def file_exists(filename: str) -> bool:
    """
    Check that sound file exists.
    """
    sound_path = get_file(filename)
    return sound_path.exists()


def play_file(filename: str) -> None:
    """
    Play a sound file.
    """
    try:
        sound_path = get_file(filename)
        play(str(sound_path), async_mode=True)

    except NavaBaseError:
        pass
