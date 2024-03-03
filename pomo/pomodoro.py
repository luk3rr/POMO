#!/usr/bin/env python

# Filename: pomodoro.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import os
import sqlite3
import socket
import time
import select

from contextlib import contextmanager

from .config import (
    SOCKFILE,
    SQL_INSERT_CMD,
    SQL_UPDATE_TABLE_CMD,
    SQL_CREATE_TABLE_CMD,
    PACKET_SIZE,
)
from .utils import Exit
from .log_manager import LogManager
from .status import Status


class Pomodoro:
    """
    Pomodoro class to keep track of the timer and the current status
    """

    def __init__(self, args):
        self.status = Status(args.worktime, args.breaktime, args.database)
        self.args = args
        self.log_manager = LogManager()

    @contextmanager
    def setup_db_connection(self, path):
        """
        Setup the connection to the database
        """
        # check if the database exist

        path = os.path.expanduser(path)

        if not os.path.isfile(path):
            self.log_manager.log(f"Database {path} does not exist, creating it...")
            with open(path, "w") as f:
                f.write("")

        session = sqlite3.connect(path)

        cur = session.cursor()
        cur.execute(SQL_CREATE_TABLE_CMD)

        self.log_manager.log(f"Connected to database: {path}")

        try:
            yield cur
        finally:
            session.commit()
            session.close()

    def save(self):
        """
        Save the current session to the database
        """
        if self.args.database:
            with self.setup_db_connection(self.args.database) as session:
                if self.status.active:
                    session.execute(SQL_INSERT_CMD)
                    self.log_manager.log("Saved session to database")
                else:
                    session.execute(SQL_UPDATE_TABLE_CMD)
                    self.log_manager.log("Updated session in database")

    @contextmanager
    def setup_listener(self):
        """
        Setup the listener for the socket
        """
        # If there's an existing socket, tell the other to exit and replace it
        self.action_exit(None, warn=False)

        # If there is a socket on disk after sending an exit request, delete it
        try:
            os.remove(SOCKFILE)
        except FileNotFoundError:
            pass

        s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        s.bind(SOCKFILE)

        try:
            yield s
        finally:
            s.close()
            # Don't try to delete the socket since at this point it could
            # be owned by a different process
            # try:
            #     os.remove(SOCKFILE)
            # except FileNotFoundError:
            #     pass

    @contextmanager
    def setup_client(self):
        """
        Setup the client for the socket
        """
        # creates socket object
        s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        s.connect(SOCKFILE)

        try:
            yield s
        finally:
            s.close()

    def wait_for_socket_cleanup(self, tries=20, wait=0.5):
        """
        Wait for the socket to be removed
        """
        for i in range(tries):
            if not os.path.isfile(SOCKFILE):
                return True
            else:
                time.sleep(wait)

        return False

    def check_actions(self, sock, status):
        """
        Check for actions on the socket
        """
        timeout = time.time() + 0.9

        data = ""

        while True:
            ready = select.select([sock], [], [], 0.2)

            if time.time() > timeout:
                break

            if ready[0]:
                try:
                    data = sock.recv(PACKET_SIZE)
                    if data:
                        break
                except socket.error as e:
                    self.log_manager.log(
                        f"Lost connection to client. Printing buffer... {e}"
                    )
                    break

        if not data:
            return

        action = data.decode("utf8")

        if action == "toggle":
            status.toggle()
            if self.args.database and self.status.status == "work":
                self.save()

        elif action == "end":
            status.next_timer()
            if self.args.database and self.status.status == "work":
                self.save()

        elif action == "lock":
            status.toggle_lock()

        elif action.startswith("time"):
            _, op, seconds = action.split(" ")
            status.change(op, seconds)

        elif action == "exit":
            raise Exit()

    def action_toggle(self, args):
        """
        Toggle the timer
        """
        with self.setup_client() as s:
            msg = "toggle"
            s.send(msg.encode("utf8"))
            self.log_manager.log("Toggled timer")

    def action_end(self, args):
        """
        End the timer
        """
        with self.setup_client() as s:
            msg = "end"
            s.send(msg.encode("utf8"))
            self.log_manager.log("Ended timer")

    def action_lock(self, args):
        """
        Lock the timer
        """
        with self.setup_client() as s:
            msg = "lock"
            s.send(msg.encode("utf8"))
            self.log_manager.log("Toggled lock")

    def action_time(self, args):
        """
        Change the timer
        """
        with self.setup_client() as s:
            msg = "time " + " ".join(args.delta)
            s.send(msg.encode("utf8"))
            self.log_manager.log(f"Changed timer by {args.delta}")

    def action_exit(self, args, warn=True):
        """
        Exit the timer
        """
        try:
            with self.setup_client() as s:
                msg = "exit"
                s.send(msg.encode("utf8"))
                self.log_manager.log("Exiting...")

        except (FileNotFoundError, ConnectionRefusedError) as e:
            if warn:
                self.log_manager.log(f"No instance of pomodoro listening, error: {e}")
        else:
            if not self.wait_for_socket_cleanup():
                self.log_manager.log("Socket was not removed, assuming it's stale")

    def action_display(self, args):
        """
        Display the timer
        """

        status = Status(self.args.worktime, self.args.breaktime, self.args.database)

        run_msg = "Pomodoro timer running..."
        print(run_msg)
        self.log_manager.log(run_msg)

        # Listen on socket
        with self.setup_listener() as sock:
            while True:
                status.update()
                status.send_status()

                try:
                    self.check_actions(sock, status)

                except Exit:
                    exit_msg = "Received exit request..."
                    print(exit_msg)
                    self.log_manager.log(exit_msg)
                    break
