#!/usr/bin/env python

# Filename: log_manager.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import datetime
import inspect

from .config import LOGFILE

CALLER_FUNCTION_NAME_LIMIT = 20


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

        # Get the calling function's name
        caller = inspect.stack()[1]
        caller_function_name = caller.function
        caller_class_name = caller.frame.f_locals.get("self", None).__class__.__name__

        # Limit the length of caller_function_name
        caller_function_name = (
            caller_function_name[:CALLER_FUNCTION_NAME_LIMIT]
            if len(caller_function_name) > CALLER_FUNCTION_NAME_LIMIT
            else caller_function_name
        )

        # Format the log message with aligned columns
        message = f"{timestamp} - {caller_class_name}::{caller_function_name:<{CALLER_FUNCTION_NAME_LIMIT}}\t-> {text}"

        with open(LOGFILE, "a") as f:
            f.write(message + "\n")
