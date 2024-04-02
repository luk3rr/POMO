#!/usr/bin/env python

# Filename: pomodoro.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import os
import socket
import time
import select
import threading

from contextlib import contextmanager

from .config import (
    SOCKFILE,
    PACKET_SIZE,
)

from .utils import Exit
from .log_manager import LogManager
from .status import Status
from .db_manager import DBManager
from .server import Server


class Pomodoro:
    """
    Pomodoro class to keep track of the timer and the current status
    """

    def __init__(self, args):
        self.status = Status(args.worktime, args.breaktime, args.tag)
        self.pending_db_update = False
        self.args = args
        self.log_manager = LogManager()
        self.db_manager = DBManager(args.database)

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
            if self.status.status == "work":
                self.db_manager.create_session(self.status.tag)
            status.toggle()

        elif action == "end":
            if self.status.status == "work":
                self.db_manager.finish_session(self.status.timer.get_real_elapsed())
            status.next_timer()

        elif action == "lock":
            status.toggle_lock()

        elif action.startswith("tag"):
            _, tag = action.split(" ")
            self.db_manager.update_tag(tag)
            status.change_tag(tag)

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

    def action_change_tag(self, args):
        """
        Change the tag
        """
        with self.setup_client() as s:
            msg = "tag " + args.tag
            s.send(msg.encode("utf8"))
            self.log_manager.log(f"Changed tag to {args.tag}")

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

        # Run server
        self.server = Server(self.status)
        self.server_thread = threading.Thread(target=self.server.run)
        self.server_thread.start()

        # Listen on socket
        with self.setup_listener() as sock:
            try:
                while True:
                    self.status.update()
                    # self.log_manager.log(f"timer: {self.status.get_timer()}")
                    # self.status.send_status()

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

        self.server_thread.join()
