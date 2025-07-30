"""Sage base clock."""

import curses
import time

from .constants import DisplayText
from .renderer import ClockRenderer
from .resize import ResizeHandler


class Clock:
    """
    Base class for all timing applications (Timer and Stopwatch).

    Provides shared functionality including:
    - Curses interface setup and teardown
    - Pause/resume functionality
    - Counter increment
    - Keyboard input handling
    - Window resize management

    This is an abstract base class - subclasses must implement _load_clock().
    """

    def __init__(self):
        self.count = 0
        self.paused = False
        self.pause_start = 0
        self.pause_time = 0
        self.refresh_rate = 0.01
        self.start_time = 0

    def load(self, **kwargs):
        """
        Initialize curses and load the application.
        """
        curses.wrapper(lambda stdscr: self._load_with_curses(stdscr, **kwargs))

    def setup_components(self, stdscr):
        """
        Set up clock component classes.
        """
        self.renderer = ClockRenderer(stdscr)
        self.resize_handler = ResizeHandler(stdscr, self.resize_redraw)
        self.resize_handler.setup()

    def setup_display(self):
        """
        Initialize the app display.
        """
        self.renderer.initialize_curses_window()
        self.renderer.render_base_features()
        self.renderer.render_counter(self.count)

    def resize_redraw(self):
        """
        Redraw the app display on window resize.
        """
        self.setup_display()
        if self.paused:
            self.renderer.render_status(DisplayText.PAUSED)

    def _load_with_curses(self, stdscr, **kwargs):
        """
        Load the application with curses initialized.
        """
        try:
            self.setup_components(stdscr)
            self.setup_display()
            self._load_clock(**kwargs)
        finally:
            self.resize_handler.cleanup()

    def _load_clock(self):
        """
        Load the clock.
        """
        raise NotImplementedError("Subclasses must implement '_load_clock'.")

    def _check_for_resize(self):
        """
        Check for window resize and handle resizing.
        """
        if self.resize_handler:
            self.resize_handler.check_and_handle()

    def _handle_pause_on_start(self, **kwargs):
        """
        Handle paused state change if --paused flag passed to clock.
        """
        if kwargs.get("paused"):
            self._on_pause()

    def _on_pause(self):
        """
        Handle paused state changes.
        """
        if not self.paused:
            self.pause_start = time.perf_counter()
            self.paused = True
            self.renderer.render_status(DisplayText.PAUSED)
        else:
            self.pause_time += time.perf_counter() - self.pause_start
            self.paused = False
            self.pause_start = 0
            self.renderer.clear_status()

    def _listen_for_keys(self):
        """
        Listen for keystrokes and handle command logic.
        """
        key = self.renderer.stdscr.getch()
        self._handle_pause(key)
        self._handle_counter(key)
        return key

    def _handle_pause(self, key):
        """
        Handle pause toggling triggered by SPACE key.
        """
        if key == ord(" "):
            self._on_pause()

    def _handle_counter(self, key):
        """
        Handle counter increment triggered by ENTER key.
        """
        if key == 10 or key == curses.KEY_ENTER:
            self.count += 1
            self.renderer.render_counter(self.count)

    def _sleep_and_refresh(self):
        """
        Handle timing and screen refresh.
        """
        time.sleep(self.refresh_rate)
        self.renderer.stdscr.refresh()

    def _get_elapsed_time(self):
        """
        Calculate the elapsed time depending on paused status.
        """
        if self.paused:
            return self.pause_start - self.start_time - self.pause_time
        return time.perf_counter() - self.start_time - self.pause_time
