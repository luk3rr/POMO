#!/usr/bin/env python3

# Filename: client.py
# Created on: March 28, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import socket
import json
import time

from .config import SERVER_SOCKFILE, PACKET_SIZE

RECONNECT_TIME = 5  # seconds

class Client:
    """
    Client class to get the status to the socket
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

        return data
