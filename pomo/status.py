#!/usr/bin/env python3

# Filename: status.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import os
import sys
import operator
import socket
import json

from .timer import Timer
from .config import SERVER_SOCKFILE, SOCKET_TIMEOUT
from .log_manager import LogManager


class Status:
    """
    Status class to keep track of the timer and the current status
    """

    def __init__(self, worktime, breaktime):
        self.worktime = worktime
        self.breaktime = breaktime
        self.status = "work"  # or "break"
        self.active = False # Pause or running
        self.timer = Timer(self.worktime)
        self.locked = True
        self.server_socket = self.setup_socket()
        self.existConection = False
        self.client_socket = None
        self.client_addr = None
        self.log_manager = LogManager()

    def __del__(self):
        self.server_socket.close()

    def setup_socket(self):
        """
        Configure the server socket
        """

        try:
            os.remove(SERVER_SOCKFILE)
        except FileNotFoundError:
            pass

        # Add server socket
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind(SERVER_SOCKFILE)
        server_socket.listen(1)
        return server_socket

    def send_status(self):
        """
        Send the status to the socket
        """

        if not self.existConection:
            self.server_socket.settimeout(SOCKET_TIMEOUT)

            try:
                self.client_socket, self.client_addr = self.server_socket.accept()
                self.existConection = True

            except socket.error:
                pass
        else:
            status_data = {
                "status": self.status,
                "timer": self.timer.format_time(),
                "active": self.active,
            }

            packet = json.dumps(status_data)

            try:
                if self.client_socket:
                    self.client_socket.send(packet.encode())

            except BrokenPipeError:
                self.log_manager.log("Lost connection to client. Waiting for new connection...")
                self.existConection = False
                self.server_socket = self.setup_socket()

    def get_timer(self):
        """
        Get the current timer
        """

        return f"{self.timer}\n"

    def show(self):
        """
        Show the current status and time
        """

        timer = self.get_timer()

        sys.stdout.write(timer)
        sys.stdout.flush()

    def toggle(self):
        """
        Toggle the timer
        """
        self.active = not self.active

    def toggle_lock(self):
        """
        Toggle the lock
        """
        self.locked = not self.locked

    def update(self):
        """
        Update the timer
        """
        if self.active:
            self.timer.update()
        # This ensures the timer counts time since the last iteration
        # and not since it was initialized
        self.timer.tick()

    def change(self, op, seconds):
        """
        Change the timer
        """
        if self.locked:
            return

        seconds = int(seconds)
        op = operator.add if op == "add" else operator.sub
        self.timer.change(op, seconds)

    def next_timer(self):
        """
        Switch to the next timer
        """
        if self.status == "work":
            if self.active:
                self.active = False
            self.status = "break"
            self.timer = Timer(self.breaktime)
        elif self.status == "break":
            self.active = False
            self.status = "work"
            self.timer = Timer(self.worktime)
