#!/usr/bin/env python3

# Filename: __main__.py
# Created on: March 29, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import argparse
import tkinter as tk

from .pomo_gui import PomodoroGUI


def parse_args():
    """
    Parse the command line arguments
    """
    parser = argparse.ArgumentParser(description="Pomodoro GUI")
    parser.add_argument("--client", action="store_true", help="Run as client")

    return parser.parse_args()


def main():
    args = parse_args()

    root = tk.Tk()
    pomodoro_gui = PomodoroGUI(root, args.client)
    root.mainloop()


if __name__ == "__main__":
    main()
