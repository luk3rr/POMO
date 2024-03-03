#!/usr/bin/env python

# Filename: integration.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import socket
import json
import time

from pomo.config import SERVER_SOCKFILE, PACKET_SIZE


# Recommended font: Noto Emoji
TOMATO = ""
BREAK = "󰅶"
PAUSE = "󱦠"
ICON_COLOR = "%{F#555}"
RESET_COLOR = "%{F-}"

RECONNECT_TIME = 5  # seconds


class Integration:
    """
    Integration class to get the status to the socket
    """

    def __init__(self):
        self.client_socket = self.connect()
        self.connection = False

    def __del__(self):
        self.close_connection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()

    def connect(self):
        """
        Connect to the server socket
        """

        while True:
            try:
                client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client_socket.connect(SERVER_SOCKFILE)
                self.connection = True
                return client_socket

            except socket.error as e:
                print(f"Error: {e}")
                time.sleep(RECONNECT_TIME)
                continue

    def reconnect(self):
        """
        Reconnect to the server socket
        """

        self.close_connection()
        self.client_socket = self.connect()

    def close_connection(self):
        """
        Close the connection
        """
        if hasattr(self, "client_socket") and self.client_socket and self.connection:
            self.client_socket.close()
            self.connection = False

    def get_status(self):
        """
        Get the status from the socket
        """

        packet = self.client_socket.recv(PACKET_SIZE).decode()

        # If no data is received, raise a timeout
        if packet == "":
            raise socket.timeout

        data = json.loads(packet)

        status = TOMATO if data["status"] == "work" else BREAK

        if not data["active"]:
            status = PAUSE

        return f"{ICON_COLOR}{status}{RESET_COLOR} {data['timer']}\n"
