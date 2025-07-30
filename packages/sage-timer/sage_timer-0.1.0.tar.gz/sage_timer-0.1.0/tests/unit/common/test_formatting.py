from sage.common.formatting import time_as_clock, time_in_english


def test_clock_format():
    """
    Test proper formatting of clock, provided given seconds.
    """
    assert time_as_clock(185) == "00:03:05"
    assert time_as_clock(25200) == "07:00:00"
    assert time_as_clock(4) == "00:00:04"
    assert time_as_clock(1500) == "00:25:00"

def test_clock_format_with_centiseconds():
    """
    Test proper formatting of clock with centiseconds.
    """
    assert time_as_clock(133.23, include_centiseconds=True) == "00:02:13:23"
    assert time_as_clock(185.11, include_centiseconds=True) == "00:03:05:11"
    assert time_as_clock(4, include_centiseconds=True) == "00:00:04:00"
    assert time_as_clock(10800.7, include_centiseconds=True) == "03:00:00:70"

def test_format_time_in_english():
    """
    Test proper formatting of time into English.
    """
    assert time_in_english(112) == "1 minute 52 seconds"
    assert time_in_english(10800) == "3 hours"
    assert time_in_english(1501) == "25 minutes 1 second"
    assert time_in_english(3960) == "1 hour 6 minutes"
