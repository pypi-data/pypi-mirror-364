import os
import subprocess


def test_update(tmp_path):
    """
    Test preset duration update.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "update", "pomodoro", "30m"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 0
    assert "success" in result.stdout.lower()


def test_update_missing_name(tmp_path):
    """
    Test preset update with missing name argument.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "update"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 2
    assert "missing argument" in result.stderr.lower()


def test_update_missing_duration(tmp_path):
    """
    Test preset update with missing duration argument.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "update", "pomodoro"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 2
    assert "missing argument" in result.stderr.lower()


def test_update_nonexistent_preset(tmp_path):
    """
    Test preset update on nonexistent preset.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "update", "pootietang", "37m"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )

    assert result.returncode == 2
    assert "not a preset" in result.stderr.lower()
