import subprocess


def test_timer_help():
    """
    Test help option on timer command.
    """
    result = subprocess.run(
        ["sage", "timer", "--help"], capture_output=True, text=True, timeout=5
    )
    assert "start a timer" in result.stdout.lower()
    assert "--paused" in result.stdout.lower()
    assert "--help" in result.stdout.lower()


def test_timer_with_duration():
    """
    Test timer with a duration as the time string.
    """
    result = subprocess.run(
        ["sage", "timer", "25m", "--test"], capture_output=True, text=True, timeout=5
    )
    assert result.returncode == 0
    assert "00:25:00" in result.stdout


def test_timer_with_preset():
    """
    Test timer with a preset as the time string.
    """
    result = subprocess.run(
        ["sage", "timer", "pomodoro", "--test"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0
    assert "00:25:00" in result.stdout


def test_timer_out_of_range_low():
    """
    Test timer duration that is less than or equal to 0 seconds raises
    error.
    """
    result = subprocess.run(
        ["sage", "timer", "0s", "--test"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert "must be greater than 0 seconds" in result.stderr.lower()


def test_timer_out_of_range_high():
    """
    Test timer duration that is greater than 24 hours raises error.
    """
    result = subprocess.run(
        ["sage", "timer", "25hr", "--test"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 2
    assert "cannot exceed 24 hours" in result.stderr.lower()
