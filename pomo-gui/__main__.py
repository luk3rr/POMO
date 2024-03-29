#!/usr/bin/env python3

# Filename: __main__.py
# Created on: March 29, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import argparse
import tkinter as tk
import pathlib

from pomo.config import DB_FILE, DEFAULT_WORKTIME, DEFAULT_BREAKTIME, DEFAULT_TAG
from .pomo_gui import PomodoroGUI


def parse_args():
    """
    Parse the command line arguments
    """
    parser = argparse.ArgumentParser(description="Pomodoro GUI")

    parser.add_argument("-c", "--client", action="store_true", help="Run as client")

    parser.add_argument(
        "-dm",
        "--darkmode", action="store_true", help="Run window in dark mode"
    )

    parser.add_argument(
        "-w",
        "--worktime",
        type=int,
        default=DEFAULT_WORKTIME,
        help="Default work timer time in seconds",
    )
    parser.add_argument(
        "-b",
        "--breaktime",
        type=int,
        default=DEFAULT_BREAKTIME,
        help="Default break timer time in seconds",
    )
    parser.add_argument(
        "-db",
        "--database", type=pathlib.Path, default=DB_FILE, help="Path to database"
    )

    parser.add_argument(
        "-t",
        "--tag",
        type=str,
        default=DEFAULT_TAG,
        help="Tag to be used to identify the timer",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    root = tk.Tk()
    pomodoro_gui = PomodoroGUI(root, args)
    root.mainloop()


if __name__ == "__main__":
    main()
