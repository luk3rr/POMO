#!/usr/bin/env python

# Filename: log_manager.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import datetime

from .config import LOGFILE

class LogManager:
    """
    Log manager class
    """
    def __init__(self):
        pass

    def __del__(self):
        pass

    def log(self, text):
        """
        Register a message in the log file
        """

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"{timestamp} {text}"

        with open(LOGFILE, "a") as f:
            f.write(message + "\n")
