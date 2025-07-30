import os
import subprocess


def test_delete(tmp_path):
    """
    Test preset deletion.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "delete", "pomodoro",],
        capture_output=True,
        text=True,
        timeout=5,
        env=env
    )

    assert result.returncode == 0
    assert "success" in result.stdout.lower()


def test_delete_missing_name(tmp_path):
    """
    Test preset deletion with missing name argument.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "delete"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env
    )

    assert result.returncode == 2
    assert "missing argument" in result.stderr.lower()


def test_delete_nonexistent_preset(tmp_path):
    """
    Test preset deletion with nonexistent preset.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "delete", "apple"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env
    )

    assert result.returncode == 2
    assert "not a preset" in result.stderr.lower()
