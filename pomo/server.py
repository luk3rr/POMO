#!/usr/bin/env python3

# Filename: server.py
# Created on: March 28, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import socket
import json
import os
import threading

from time import sleep
from .config import SERVER_SOCKFILE
from .log_manager import LogManager


class Server:
    """
    Server class to handle the server socket
    """

    def __init__(self, status):
        self.status = status
        self.log_manager = LogManager()
        self.total_clients = 0

    def __del__(self):
        pass

    def run(self):
        """
        Run the server
        """
        while True:
            self.setup_socket()

    def setup_socket(self):
        """
        Configure the server socket
        """

        try:
            os.remove(SERVER_SOCKFILE)

        except FileNotFoundError:
            pass

        # Add server socket
        try:
            server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server_socket.bind(SERVER_SOCKFILE)
            server_socket.listen()

            # server_socket.settimeout(SOCKET_TIMEOUT)

            while True:
                client_socket, client_addr = server_socket.accept()
                self.log_manager.log(f"Server socket created")

                self.total_clients += 1
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_addr, self.total_clients),
                )
                thread.start()

        except Exception as e:
            self.log_manager.log(f"Error: {e}")

        finally:
            server_socket.close()

    def handle_client(self, client_socket, client_addr, client_id):
        """
        Handle the client socket
        """
        try:
            while True:
                sleep(1)
                status_data = {
                    "status": self.status.status,
                    "timer": self.status.timer.format_time(),
                    "active": self.status.active,
                    "remaining": (
                        self.status.worktime - self.status.timer.get_elapsed()
                        if self.status.status == "work"
                        else self.status.breaktime - self.status.timer.get_elapsed()
                    ),
                    "tag": self.status.tag,
                    "total_time": (
                        self.status.worktime
                        if self.status.status == "work"
                        else self.status.breaktime
                    ),
                }

                packet = json.dumps(status_data)

                client_socket.send(packet.encode())

        except BrokenPipeError:
            self.log_manager.log(f"Lost connection to client {client_id}")

        finally:
            self.total_clients -= 1
            client_socket.close()
