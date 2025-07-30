"""Sage renderer class for curses interface."""

import curses

from .constants import DisplayText


class ClockRenderer:
    """
    Handles all curses-based rendering for timer and stopwatch displays.

    The ClockRenderer manages the terminal UI including clock display, status
    messages, help text, and color schemes. It calculates positioning and
    handles text centering automatically.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self._setup_colors()

    @staticmethod
    def _setup_colors():
        """
        Initialize curses color pairs.
        """
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    def get_center_coordinates(self, text: str) -> tuple[int, int]:
        """
        Calculate center coordinates of the curses window.
        """
        max_y, max_x = self.stdscr.getmaxyx()

        y = max_y // 2
        x = (max_x // 2) - (len(text) // 2)

        # an even numbered text length can't be centered perfectly, so
        # offset y to the left by one character if the text length
        # is an even number.
        x = x - 1 if len(text) % 2 else x

        return (y, x)

    def initialize_curses_window(self):
        """
        Initial curses window configuration.
        """
        self.stdscr.clear()
        curses.curs_set(0)
        self.stdscr.nodelay(1)

    def render_base_features(self):
        """
        Render base clock features
        """
        self.render_app_title()
        self.render_help_text()

    def render_app_title(self):
        """
        Render the application title at the top left of the curses
        window.
        """
        self.stdscr.addstr(1, 1, DisplayText.TITLE, curses.color_pair(2))

    def render_clock(self, time_text: str):
        """
        Render the clock at the center of the curses window.
        """
        y, x = self.get_center_coordinates(time_text)
        self.stdscr.addstr(y, x, time_text, curses.color_pair(1))

    def render_status(self, status_text: str):
        """
        Render the clock status directly below the clock in the curses
        window.
        """
        y, x = self.get_center_coordinates(status_text)
        self.stdscr.addstr(y + 1, x, status_text, curses.color_pair(4))

    def clear_status(self):
        """
        Clear the status text.
        """
        y, _ = self.get_center_coordinates("")
        self.stdscr.move(y + 1, 0)
        self.stdscr.clrtoeol()

    def render_help_text(self, help_text = DisplayText.RUNNING_HELP):
        """
        Render the help text at the bottom left of the curses window.
        """
        y, _ = self.stdscr.getmaxyx()
        self.stdscr.addstr(y - 1, 1, help_text, curses.color_pair(3))

    def clear_help_text(self, help_text = DisplayText.RUNNING_HELP):
        """
        Clear the help text at the bottom left of the curses window.
        """
        y, _ = self.stdscr.getmaxyx()
        empty_string = " " * len(help_text)
        self.stdscr.addstr(y - 1, 1, empty_string)

    def render_heading(self, heading_text: str):
        """
        Render the timer heading above the clock in the curses window.
        """
        y, x = self.get_center_coordinates(heading_text)
        self.stdscr.addstr(y - 1, x, heading_text, curses.color_pair(2))

    def render_counter(self, count = 0):
        """
        Render the counter at the bottom right of the curses window.
        """
        counter_text = f"Counter: {count}"
        y, x = self.stdscr.getmaxyx()
        x -= len(counter_text)
        self.stdscr.addstr(y - 1, x - 1, counter_text, curses.color_pair(3))

    def render_warning(self, warning_text: str):
        """
        Render warning text in upper right corner of screen.
        """
        _, x = self.stdscr.getmaxyx()
        x -= len(warning_text)
        self.stdscr.addstr(1, x - 1, warning_text, curses.color_pair(4))

    def render_times_up_display(self):
        """
        Render display for timer completion state.
        """
        self.render_status(DisplayText.TIMES_UP)
        self.stdscr.nodelay(0)
        self.clear_help_text()
        self.render_help_text(DisplayText.TIMES_UP_HELP)
