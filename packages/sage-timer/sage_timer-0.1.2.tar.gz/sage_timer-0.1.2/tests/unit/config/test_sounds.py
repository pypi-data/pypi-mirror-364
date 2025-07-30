from sage.config import sounds


def test_sound_exists():
    """
    Test for file existence in sounds directory.
    """
    assert sounds.file_exists("timesup.mp3")
    assert not sounds.file_exists("nothing.mp3")
