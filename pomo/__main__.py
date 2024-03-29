#!/usr/bin/env python3

# Filename: __main__.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import argparse
import pathlib

from .validate_time import ValidateTime
from .config import DB_FILE, DEFAULT_WORKTIME, DEFAULT_BREAKTIME, DEFAULT_TAG
from .pomodoro import Pomodoro


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pomodoro timer to be used with polybar"
    )
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
        "--database", type=pathlib.Path, default=DB_FILE, help="Path to database"
    )

    parser.add_argument(
        "--tag",
        type=str,
        default=DEFAULT_TAG,
        help="Tag to be used to identify the timer",
    )

    parser.set_defaults(func=None)

    sub = parser.add_subparsers(dest="action")

    toggle = sub.add_parser("toggle", help="start/stop timer")
    end = sub.add_parser("end", help="end current timer")
    lock = sub.add_parser("lock", help="lock time actions - prevent changing time")
    exit = sub.add_parser(
        "exit", help="exit any listening polypomo instances gracefully"
    )
    tag = sub.add_parser("tag", help="change the tag of the current timer")
    tag.add_argument("tag", help="New tag to be used")

    time = sub.add_parser("time", help="add/remove time to current timer")
    time.add_argument(
        "delta",
        action=ValidateTime,
        help="Time to add/remove to current timer (in seconds)",
    )

    return parser.parse_args()


def main():
    """
    Main function
    """
    args = parse_args()

    pomodoro = Pomodoro(args)

    actions = {
        "toggle": pomodoro.action_toggle,
        "end": pomodoro.action_end,
        "lock": pomodoro.action_lock,
        "exit": pomodoro.action_exit,
        "time": pomodoro.action_time,
        "tag": pomodoro.action_change_tag,
        None: pomodoro.action_display,
    }

    action_func = actions.get(args.action, pomodoro.action_display)
    action_func(args)


if __name__ == "__main__":
    main()
