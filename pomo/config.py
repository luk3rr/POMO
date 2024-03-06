#!/usr/bin/env python3

# Filename: config.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import os

SOCKDIR = os.environ.get("XDG_RUNTIME_DIR", "/var/tmp")
SOCKFILE = os.path.join(SOCKDIR, "pomo.sock")
SERVER_SOCKFILE = os.path.join(SOCKDIR, "server-pomo.sock")

LOGFILE = "/tmp/pomo.log"
DB_FILE = "~/Documents/pomo.db"
DEFAULT_TAG = "other"

DAY_FACTOR = 86400
HOUR_FACTOR = 3600
MINUTE_FACTOR = 60
GMT_OFFSET = -3 # Greenwich Mean Time

DEFAULT_WORKTIME = 40 * MINUTE_FACTOR
DEFAULT_BREAKTIME = 10 * MINUTE_FACTOR

PACKET_SIZE = 1024
SOCKET_TIMEOUT = 1e-6
