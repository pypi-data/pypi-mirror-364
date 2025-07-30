import os
import subprocess


def test_version():
    """
    Test sage version option.
    """
    result = subprocess.run(
        ["sage", "--version"], capture_output=True, text=True, timeout=5
    )

    assert "sage, version 0.1.0" in result.stdout


def test_help():
    """
    Test sage help option.
    """
    result = subprocess.run(
        ["sage", "--help"], capture_output=True, text=True, timeout=5
    )

    assert "--version" in result.stdout.lower()
    assert "--help" in result.stdout.lower()
    assert "timer" in result.stdout.lower()
    assert "stopwatch" in result.stdout.lower()
