#!/usr/bin/env python3

# Filename: status.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import sys
import operator
import subprocess

from .timer import Timer
from .config import ICON
from .log_manager import LogManager


class Status:
    """
    Status class to keep track of the timer and the current status
    """

    def __init__(self, worktime, breaktime, tag):
        self.worktime = worktime
        self.breaktime = breaktime
        self.status = "work"  # or "break"
        self.tag = tag
        self.active = False  # Pause or running
        self.timer = Timer(self.worktime, self.tag, self.status)
        self.locked = True
        self.log_manager = LogManager()

    def __del__(self):
        pass

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
            if self.is_system_active():
                self.log_manager.log("System is in suspend. Pausing timer...")
                self.toggle()

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
            self.timer = Timer(self.breaktime, self.tag, self.status)
        elif self.status == "break":
            self.active = False
            self.status = "work"
            self.timer = Timer(self.worktime, self.tag, self.status)

    def change_tag(self, tag):
        """
        Change the tag of the current session
        """
        old_tag = self.tag
        self.tag = self.sanitize_tag(tag)
        self.timer.update_tag(self.tag)

        self.log_manager.log(f"Updated tag from {old_tag} to {self.tag}")

        try:
            subprocess.call(
                [
                    "notify-send",
                    "-t",
                    "5000",
                    "-u",
                    "normal",
                    "-i",
                    ICON.TOMATO,
                    "Pomodoro",
                    f"Updated tag to '{self.tag}'",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            # Skip if notify-send isn't installed
            pass

    def sanitize_tag(self, tag):
        """
        Sanitize the tag
        Gets only the first word of the tag
        """
        return tag.split(" ")[0]

    def is_system_active(self):
        """
        Check if the system is in suspend
        """
        try:
            result = subprocess.run(
                [
                    "systemctl",
                    "is-active",
                    "sleep.target",
                    "suspend.target",
                    "hibernate.target",
                ],
                capture_output=True,
                text=True,
            ).stdout.split("\n")

            return "active" in result

        except subprocess.CalledProcessError:
            return False
