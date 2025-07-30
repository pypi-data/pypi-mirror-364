"""Sage stopwatch implementation."""

import time

from .clock import Clock
from sage.common.formatting import time_as_clock


class Stopwatch(Clock):
    """
    A stopwatch that counts up from zero with centisecond precision.

    The Stopwatch class provides elapsed time tracking functionality
    with a curses-based-display. It inherits from Clock for shared
    functionality like pause/resume and counter increment.
    """

    def _load_clock(self, **kwargs):
        """
        Initialize and start the stopwatch.
        """
        self._initialize_stopwatch()
        self._handle_pause_on_start(**kwargs)
        self._start()

    def _initialize_stopwatch(self):
        """
        Initialize stopwatch settings.
        """
        self.start_time = time.perf_counter()

    def _start(self):
        """
        Start the stopwatch.
        """
        while self._listen_for_keys() != ord("q"):
            self._check_for_resize()
            self._update_display()
            self._sleep_and_refresh()

    def _update_display(self):
        """
        Update the stopwatch display.
        """
        display_time = self._get_display_time()
        self.renderer.render_clock(display_time)

    def _get_display_time(self):
        """
        Calculate the display time.
        """
        time_elapsed = self._get_elapsed_time()
        return time_as_clock(time_elapsed, include_centiseconds=True)
