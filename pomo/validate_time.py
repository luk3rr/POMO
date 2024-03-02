#!/usr/bin/env python3

# Filename: validate_time.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import argparse


class ValidateTime(argparse.Action):
    """
    Validate time format
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if values[0] not in "-+":
            parser.error(
                "Time format should be +num or -num to add or remove time, respectively"
            )
        if not values[1:].isdigit():
            parser.error("Expected number after +/- but saw '{}'".format(values[1:]))

        # action = operator.add if values[0] == '+' else operator.sub
        # value = int(values[1:])
        action = "add" if values[0] == "+" else "sub"
        value = values[1:]

        setattr(namespace, self.dest, (action, value))
