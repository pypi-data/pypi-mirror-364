import subprocess


def test_list():
    """
    Test list command lists all presets.
    """
    result = subprocess.run(
        ["sage", "list"], capture_output=True, text=True, timeout=5
    )

    assert result.returncode == 0
    assert "pomodoro" in result.stdout
    assert "johncage" in result.stdout
    assert "potato" in result.stdout
    assert "pika" in result.stdout


def test_list_help():
    """
    Test help option on list command.
    """
    result = subprocess.run(
        ["sage", "list", "--help"], capture_output=True, text=True, timeout=5
    )

    assert result.returncode == 0
    assert "--help" in result.stdout
    assert "list all presets"
