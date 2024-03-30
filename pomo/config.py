#!/usr/bin/env python3

# Filename: config.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import os

SOCKDIR = os.environ.get("XDG_RUNTIME_DIR", "/var/tmp")
SOCKFILE = os.path.join(SOCKDIR, "pomo.sock")
SERVER_SOCKFILE = os.path.join(SOCKDIR, "server-pomo.sock")

LOGFILE = "/tmp/pomo.log"
DB_FILE = "~/.config/pomo/pomo.db"
DB_TABLE_NAME = "sessions"

DEFAULT_TAG = "other"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the sound player
PLAYER = "paplay"

DAY_FACTOR = 86400
HOUR_FACTOR = 3600
MINUTE_FACTOR = 60
GMT_OFFSET = -3  # Greenwich Mean Time

DEFAULT_WORKTIME = 40 * MINUTE_FACTOR
DEFAULT_BREAKTIME = 10 * MINUTE_FACTOR

PACKET_SIZE = 1024
SOCKET_TIMEOUT = 1e-6


class SOUND:
    """
    Class to store the sounds
    """

    BELL = os.path.join(SCRIPT_DIR, "../data/sounds/bell.ogg")
    TIMER = os.path.join(SCRIPT_DIR, "../data/sounds/timer.ogg")


class ICON:
    """
    Class to store the icons
    """

    TOMATO = os.path.join(SCRIPT_DIR, "../data/img/tomato.png")
    MOON = os.path.join(SCRIPT_DIR, "../data/img/moon.png")
    SUN = os.path.join(SCRIPT_DIR, "../data/img/sun.png")
    PAUSE_DARK = os.path.join(SCRIPT_DIR, "../data/img/pause_dark.png")
    PAUSE_LIGHT = os.path.join(SCRIPT_DIR, "../data/img/pause_light.png")
    PLAY_DARK = os.path.join(SCRIPT_DIR, "../data/img/play_dark.png")
    PLAY_LIGHT = os.path.join(SCRIPT_DIR, "../data/img/play_light.png")
    SKIP_DARK = os.path.join(SCRIPT_DIR, "../data/img/skip_dark.png")
    SKIP_LIGHT = os.path.join(SCRIPT_DIR, "../data/img/skip_light.png")
