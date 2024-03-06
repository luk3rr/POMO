#!/usr/bin/env python3

# Filename: timer.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import time
from subprocess import call, DEVNULL, Popen

from .log_manager import LogManager

from .config import (
    DAY_FACTOR,
    HOUR_FACTOR,
    MINUTE_FACTOR,
    BELL_SOUND,
    TIMER_SOUND,
    PLAYER,
)


class Timer:
    """
    Timer class to keep track of the time
    """

    def __init__(self, remtime):
        self.total = remtime
        self.time = remtime
        self.notified = False
        self.sound_played = False
        self.tick()
        self.log_manager = LogManager()

    def __str__(self):
        return self.format_time()

    def tick(self):
        """
        Update the previous time to the current time
        """
        self.previous = time.time()

    def format_time(self):
        """
        Format the time to a string
        """
        if self.time > 0:
            rem = self.time
            neg = ""
        else:
            rem = -self.time
            neg = "-"

        days = int(rem // DAY_FACTOR)
        rem -= days * DAY_FACTOR
        hours = int(rem // HOUR_FACTOR)
        rem -= hours * HOUR_FACTOR
        minutes = int(rem // MINUTE_FACTOR)
        rem -= minutes * MINUTE_FACTOR
        seconds = int(rem // 1)

        strtime = []
        if days > 0:
            strtime.append(str(days))

        if days > 0 or hours > 0:
            strtime.append("{:02d}".format(hours))

        # Always append minutes and seconds
        strtime.append("{:02d}".format(minutes))
        strtime.append("{:02d}".format(seconds))

        return neg + ":".join(strtime)

    def update(self):
        """
        Update the timer
        """
        now = time.time()
        delta = now - self.previous
        self.time -= delta

        if self.time < 4 and not self.sound_played:
            self.play_sound(TIMER_SOUND)
            self.sound_played = True

        # Send a notification when timer reaches 0
        if not self.notified and self.time < 0:
            self.notified = True
            try:
                call(
                    [
                        "notify-send",
                        "-t",
                        "0",
                        "-u",
                        "critical",
                        "Pomodoro",
                        "Timer reached zero",
                    ],
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                )

                self.play_sound(BELL_SOUND)
            except FileNotFoundError:
                # Skip if notify-send isn't installed
                pass

    def change(self, op, seconds):
        """
        Change the time
        """
        self.time = op(self.time, seconds)

    def get_elapsed(self):
        """
        Get the elapsed time
        """
        return self.total - self.time

    def play_sound(self, sound):
        """
        Play a sound asynchronously
        """
        try:
            Popen([PLAYER, sound], stdout=DEVNULL, stderr=DEVNULL)
            self.log_manager.log(f"Playing sound {sound}")
        except Exception as e:
            self.log_manager.log(f"Error playing sound {sound}")
            self.log_manager.log(f"Error message: {str(e)}")
