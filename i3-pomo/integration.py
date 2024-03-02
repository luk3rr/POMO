#!/usr/bin/env python

# Filename: integration.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import socket


from pomo.config import SERVER_SOCKFILE


class Integration:
    """
    Integration class to get the status to the socket
    """

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if not self.connect():
            raise Exception("Could not connect to the server socket")

    def __del__(self):
        self.client_socket.close()

    def connect(self):
        """
        Connect to the server socket
        """
        try:
            self.client_socket.connect(SERVER_SOCKFILE)
            return True
        except socket.error as e:
            print(f"Error: {e}")
            return False

    def get_status(self):
        """
        Get the status from the socket
        """

        try:
            return self.client_socket.recv(1024).decode()

        except socket.timeout:
            return "No data received"
