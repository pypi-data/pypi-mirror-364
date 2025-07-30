"""Sage clock resize handler"""

import curses
import signal
import threading


class ResizeHandler:
    """
    Manages terminal window resize events for curses applications.

    Uses signal handling to detect SIGWINCH events and coordinate with the
    main application to redraw the interface when the terminal is resized.
    """

    def __init__(self, stdscr, redraw_callback):
        self.stdscr = stdscr
        self.redraw_callback = redraw_callback
        self.resize_flag = threading.Event()
        self.old_handler = None

    def setup(self):
        """
        Setup window resize signal handler.
        """
        self.old_handler = signal.signal(signal.SIGWINCH, self._handle_resize)

    def cleanup(self):
        """
        Restore the original signal handler.
        """
        if self.old_handler:
            signal.signal(signal.SIGWINCH, self.old_handler)

    def _handle_resize(self, signum, frame):
        """
        Set a flag that resize occurred.
        """
        self.resize_flag.set()

    def check_and_handle(self):
        """
        Check if resize occurred and redraw if so.
        """
        if self.resize_flag.is_set():
            self.resize_flag.clear()
            curses.endwin()
            self.stdscr.refresh()
            self.redraw_callback()
