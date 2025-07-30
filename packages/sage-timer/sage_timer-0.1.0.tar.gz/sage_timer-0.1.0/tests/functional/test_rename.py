import os
import subprocess


def test_rename(tmp_path):
    """
    Test preset rename.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "rename", "pomodoro", "pineapple"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env
    )

    assert result.returncode == 0
    assert "success" in result.stdout.lower()


def test_rename_without_new_name(tmp_path):
    """
    Test preset rename without new name.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "rename", "pomodoro"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env
    )

    assert result.returncode == 2
    assert "missing argument" in result.stderr.lower()


def test_rename_with_nonexistent_name(tmp_path):
    """
    Test preset rename with nonexistent preset.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "rename", "potomac", "potato"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env
    )

    assert result.returncode == 2
    assert "not a preset" in result.stderr.lower()
