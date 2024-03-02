#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Filename: __main__.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import argparse
import pathlib

from .status import (
    action_display,
    action_toggle,
    action_time,
    action_end,
    action_exit,
    action_lock,
)

from .validate_time import ValidateTime
from .config import DEFAULT_WORKTIME, DEFAULT_BREAKTIME


def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Pomodoro timer to be used with polybar"
    )
    # Display - main loop showing status
    parser.add_argument(
        "--worktime",
        type=int,
        default=DEFAULT_WORKTIME,
        help="Default work timer time in seconds",
    )
    parser.add_argument(
        "--breaktime",
        type=int,
        default=DEFAULT_BREAKTIME,
        help="Default break timer time in seconds",
    )
    parser.add_argument(
        "--saveto", type=pathlib.Path, default=None, help="Path to database"
    )
    parser.set_defaults(func=action_display)

    sub = parser.add_subparsers()

    # start/stop timer
    toggle = sub.add_parser("toggle", help="start/stop timer")
    toggle.set_defaults(func=action_toggle)

    # end timer
    end = sub.add_parser("end", help="end current timer")
    end.set_defaults(func=action_end)

    # lock timer changes
    lock = sub.add_parser("lock", help="lock time actions - prevent changing time")
    lock.set_defaults(func=action_lock)

    # lock timer changes
    exit = sub.add_parser(
        "exit", help="exit any listening polypomo instances gracefully"
    )
    exit.set_defaults(func=action_exit)

    # change timer
    time = sub.add_parser("time", help="add/remove time to current timer")
    time.add_argument(
        "delta",
        action=ValidateTime,
        help="Time to add/remove to current timer (in seconds)",
    )
    time.set_defaults(func=action_time)

    return parser.parse_args()


def main():
    """
    Main function
    """
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
