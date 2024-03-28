#!/usr/bin/env python

# Filename: polypomo.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import socket
import json

from pomo.client import Client

# Recommended font: Noto Emoji
TOMATO = ""
BREAK = "󰅶"
PAUSE = "󱦠"
ICON_COLOR = "%{F#555}"
RESET_COLOR = "%{F-}"

class PolyPomo:
    """
    """

    def __init__(self):
        self.client = Client()

    def __del__(self):
        self.client.close_connection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close_connection()


    def display(self):
        """
        """

        try:
            data = self.client.get_status()

        except socket.timeout:
            self.client.reconnect()
            return f"Connection lost. Reconnecting...\n"

        except json.JSONDecodeError:
            # return f"Failed to decode data"
            return ""

        status = TOMATO if data["status"] == "work" else BREAK

        if not data["active"]:
            status = PAUSE

        return f"{ICON_COLOR}{status}{RESET_COLOR}  {data['timer']}\n"
