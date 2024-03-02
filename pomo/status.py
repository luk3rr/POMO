#!/usr/bin/env python3

# Filename: status.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import os
import sys
import operator
import sqlite3
import socket
import time
import select
import threading

from contextlib import contextmanager
from .timer import Timer
from .config import SOCKFILE, SERVER_SOCKFILE
from .utils import Exit

# Recommended font: Noto Emoji
TOMATO = ""
BREAK = "󰅶"
PAUSE = "󱦠"
ICON_COLOR = "%{F#555}"
RESET_COLOR = "%{F-}"


class Status:
    """
    Status class to keep track of the timer and the current status
    """

    def __init__(self, worktime, breaktime, saveto):
        self.worktime = worktime
        self.breaktime = breaktime
        self.status = "work"  # or "break"
        self.timer = Timer(self.worktime)
        self.active = False
        self.locked = True
        self.saveto = saveto
        self.server_socket = self.setup_socket()
        self.existConection = False
        self.client_socket = None
        self.client_addr = None

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

    def send_status(self, msg):
        """
        Send the status to the socket
        """

        if not self.existConection:
            self.server_socket.settimeout(1e-6)
            try:
                self.client_socket, self.client_addr = self.server_socket.accept()
                self.existConection = True
            except socket.error:
                pass
        else:
            try:
                self.client_socket.send(msg.encode())
            except BrokenPipeError:
                print("Lost connection to client. Exiting...")
                self.existConection = False

    def get_status_msg(self):
        """
        Get the status message
        """
        status = TOMATO if self.status == "work" else BREAK
        if not self.active:
            status = PAUSE

        return f"{ICON_COLOR}{status}{RESET_COLOR} {self.timer}\n"

    def show(self):
        """
        Show the current status and time
        """
        status = TOMATO if self.status == "work" else BREAK
        if not self.active:
            status = PAUSE

        msg = self.get_status_msg()

        sys.stdout.write(msg)
        sys.stdout.flush()

        self.send_status(msg)

    def toggle(self):
        """
        Toggle the timer
        """
        self.active = not self.active
        if self.saveto and self.status == "work":
            self.save()

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
                self.save()  # save before switching if toggle didn't get called
            self.status = "break"
            self.timer = Timer(self.breaktime)
        elif self.status == "break":
            self.active = False
            self.status = "work"
            self.timer = Timer(self.worktime)

    def save(self):
        """
        Save the current session to the database
        """
        if self.saveto:
            with setup_conn(self.saveto) as conn:
                if self.active:
                    conn.execute(
                        "INSERT INTO sessions VALUES (date('now'), time('now'), NULL, NULL)"
                    )
                else:
                    conn.execute(
                        """UPDATE sessions
                           SET stop = time('now')
                           WHERE start IN (
                             SELECT start FROM sessions
                             ORDER BY start DESC
                             LIMIT 1)
                        """
                    )


@contextmanager
def setup_conn(path):
    """
    Setup the connection to the database
    """
    # check if the database exist
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS sessions (
             date text,
             start text,
             stop text,
             project text,
        )"""
    )
    try:
        yield cur
    finally:
        conn.commit()
        conn.close()


@contextmanager
def setup_listener():
    """
    Setup the listener for the socket
    """
    # If there's an existing socket, tell the other to exit and replace it
    action_exit(None, warn=False)

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
def setup_client():
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

    # tm = s.recv(1024)  # msg can only be 1024 bytes long


def wait_for_socket_cleanup(tries=20, wait=0.5):
    """
    Wait for the socket to be removed
    """
    for i in range(tries):
        if not os.path.isfile(SOCKFILE):
            return True
        else:
            time.sleep(wait)

    return False


def check_actions(sock, status):
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
                data = sock.recv(1024)
                if data:
                    break
            except socket.error as e:
                # TODO replace this by logging
                print("Lost connection to client. Printing buffer...", e)
                break

    if not data:
        return

    action = data.decode("utf8")
    if action == "toggle":
        status.toggle()
    elif action == "end":
        status.next_timer()
    elif action == "lock":
        status.toggle_lock()
    elif action.startswith("time"):
        _, op, seconds = action.split(" ")
        status.change(op, seconds)
    elif action == "exit":
        raise Exit()


def action_toggle(args):
    """
    Toggle the timer
    """
    # TODO logging = print("Running toggle", args)
    with setup_client() as s:
        msg = "toggle"
        s.send(msg.encode("utf8"))


def action_end(args):
    """
    End the timer
    """
    # TODO logging = print("Running end", args)
    with setup_client() as s:
        msg = "end"
        s.send(msg.encode("utf8"))


def action_lock(args):
    """
    Lock the timer
    """
    # TODO logging = print("Running lock", args)
    with setup_client() as s:
        msg = "lock"
        s.send(msg.encode("utf8"))


def action_time(args):
    """
    Change the timer
    """
    # TODO logging = print("Running time", args)
    with setup_client() as s:
        msg = "time " + " ".join(args.delta)
        s.send(msg.encode("utf8"))


def action_exit(args, warn=True):
    """
    Exit the timer
    """
    # TODO logging = print("Running exit", args)
    try:
        with setup_client() as s:
            msg = "exit"
            s.send(msg.encode("utf8"))
    except (FileNotFoundError, ConnectionRefusedError) as e:
        if warn:
            print("No instance of polypomo listening, error:", e)
    else:
        if not wait_for_socket_cleanup():
            print("Socket was not removed, assuming it's stale")


def action_display(args):
    """
    Display the timer
    """
    # TODO logging = print("Running display", args)

    status = Status(args.worktime, args.breaktime, args.saveto)

    # Listen on socket
    with setup_listener() as sock:
        while True:
            status.show()
            status.update()
            try:
                check_actions(sock, status)
            except Exit:
                print("Received exit request...")
                break
