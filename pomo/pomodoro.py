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
        self.status = Status(args.worktime, args.breaktime)
        self.pending_db_update = False
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
        cur.execute(
            """CREATE TABLE IF NOT EXISTS sessions (
                            date TEXT,
                            start TEXT,
                            duration TEXT,
                            tag TEXT);
                       """
        )

        self.log_manager.log(f"Connected to database: {path}")

        try:
            yield cur
        finally:
            self.log_manager.log("Closing database connection")
            session.commit()
            session.close()

    def save(self, opcode="s"):
        """
        Save the current session to the database

        opcode: str
            s: save
            u: update
        """
        self.log_manager.log(f"{self.status.status} {opcode}")
        if self.status.status == "work":
            with self.setup_db_connection(self.args.database) as session:
                if opcode == "s" and not self.pending_db_update:
                    session.execute(
                        "INSERT INTO sessions VALUES (date('now'), time('now'), NULL, NULL);"
                    )
                    self.log_manager.log("Saved session to database")
                    self.pending_db_update = True

                elif opcode == "u" and self.pending_db_update:
                    duration = self.status.timer.get_elapsed()
                    session.execute(
                        f"""UPDATE sessions
                          SET duration = '{duration}'
                          WHERE start IN (
                             SELECT start FROM sessions
                             ORDER BY start DESC
                             LIMIT 1);
                        """
                    )
                    self.log_manager.log("Updated session in database")
                    self.pending_db_update = False

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
            self.save(opcode="s")
            status.toggle()

        elif action == "end":
            self.save(opcode="u")
            status.next_timer()

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
        run_msg = "Pomodoro timer running..."
        print(run_msg)
        self.log_manager.log(run_msg)

        # Listen on socket
        with self.setup_listener() as sock:
            try:
                while True:
                    self.status.update()
                    self.status.send_status()

                    try:
                        self.check_actions(sock, self.status)

                    except Exit:
                        exit_msg = "Received exit request..."
                        print(exit_msg)
                        self.log_manager.log(exit_msg)
                        break

            # Ctrl+C
            except KeyboardInterrupt:
                keyboard_msg = "Keyboard interrupt received, exiting..."
                self.log_manager.log(keyboard_msg)
                print(keyboard_msg)
