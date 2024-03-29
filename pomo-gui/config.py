#!/usr/bin/env python3

# Filename: config.py
# Created on: March 29, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>


class BUTTON:
    IMG_SIZE = (30, 30)


class WINDOW:
    FONT_SIZE = 24
    TITLE = "Pomodoro Timer"
    SIZE = "300x420"
    FONT = "Helvetica"
    UPDATE_INTERVAL_MS = 1000


class CLOCK:
    SIZE = (200, 200)
    FONT_SIZE = 36
    WINDOW_SIZE = (100, 100)


class TAG:
    FONT_SIZE = 12
    WINDOW_SIZE = (100, 135)


class ARC:
    CENTER = (100, 100)
    RADIUS = 80
    WIDTH = 10
    START_ANGLE = 90
    EXTEND_ANGLE = 360
    TAG = "progress_circle"


class DRACULA_THEME:
    """
    Class to store the Dracula theme colors
    reference: https://draculatheme.com/contribute
    """

    BACKGROUND = "#282A36"
    CURRENT_LINE = "#44475A"
    FOREGROUND = "#F8F8F2"
    COMMENT = "#6272A4"
    CYAN = "#8BE9FD"
    GREEN = "#50FA7B"
    ORANGE = "#FFB86C"
    PINK = "#FF79C6"
    PURPLE = "#BD93F9"
    RED = "#FF5555"
    YELLOW = "#F1FA8C"


class COLOR:
    """
    Class to store the colors
    """

    BLACK = "#000000"
    WHITE = "#FFFFFF"
    GRAY = "#D8D8D8"
    RED = "#FF6347"
    GREEN = "#4CAF50"
    BLUE = "#009bff"
