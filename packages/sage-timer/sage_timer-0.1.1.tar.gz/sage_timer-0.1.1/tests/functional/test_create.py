import os
import subprocess


def test_create(tmp_path):
    """
    Test preset creation.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "create", "rice", "15m"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )
    assert result.returncode == 0
    assert "success" in result.stdout.lower()
    assert "rice" in result.stdout

    # Verify that preset is in preset list.
    result = subprocess.run(
        ["sage", "list"], capture_output=True, text=True, timeout=5, env=env
    )
    assert "rice" in result.stdout.lower()
    assert "15 minutes" in result.stdout.lower()


def test_create_duplicate_name(tmp_path):
    """
    Test preset creation with existing preset name.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "create", "pomodoro", "45m"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )
    assert result.returncode == 2
    assert "already a preset" in result.stderr.lower()


def test_create_without_duration(tmp_path):
    """
    Test preset creation without duration argument.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "create", "nothing"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )
    assert result.returncode == 2
    assert "missing argument" in result.stderr.lower()


def test_create_out_of_range_high(tmp_path):
    """
    Test preset creation without duration argument.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "create", "bigones", "25hr"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )
    assert result.returncode == 2
    assert "cannot exceed 24 hours" in result.stderr.lower()


def test_create_out_of_range_low(tmp_path):
    """
    Test preset creation without duration argument.
    """
    env = os.environ.copy()
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        ["sage", "create", "littleones", "0s"],
        capture_output=True,
        text=True,
        timeout=5,
        env=env,
    )
    assert result.returncode == 2
    assert "must be greater than 0 seconds" in result.stderr.lower()
