#!/usr/bin/env python

# Filename: log_manager.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import datetime
import inspect
import re

from .config import LOGFILE


class LogManager:
    """
    Log manager class
    """

    def __init__(self):
        pass

    def __del__(self):
        pass

    def sanitize_message(self, text):
        """
        Sanitize the message
        """

        text = text.replace("\n", " ")  # Remove newlines
        text = re.sub(r"\s+", " ", text)  # Remove multiple spaces

        return text

    def log(self, text, level="INFO"):
        """
        Register a message in the log file
        """

        text = self.sanitize_message(text)

        timestamp = datetime.datetime.now().strftime("%a %Y-%m-%d %H:%M:%S")

        # Get the calling function's name
        caller = inspect.stack()[1]
        caller_function_name = caller.function
        caller_class_name = caller.frame.f_locals.get("self", None).__class__.__name__

        # Format the log message with aligned columns
        message = f"[{timestamp}] [{level}] {caller_class_name}::{caller_function_name} : {text}"

        with open(LOGFILE, "a") as f:
            f.write(message + "\n")
