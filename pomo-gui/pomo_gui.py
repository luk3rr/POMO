#!/usr/bin/env python3

# Filename: pomo_gui.py
# Created on: March 28, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import tkinter as tk
import socket
import json
import subprocess

from tkinter import ttk
from PIL import Image, ImageTk

from pomo.client import Client
from pomo.config import COLOR, ICON


class PomodoroGUI:
    def __init__(self, master, run_as_client=False):
        self.master = master

        if run_as_client:
            self.client = Client()
        else:
            self.start_pomo_server()
            self.client = Client()

        self.status = "Pause"
        self.draw_gui()
        self.display()

    def __del__(self):
        if self.process_child:
            # Terminates the process
            self.process_child.terminate()

    def start_pomo_server(self):
        """
        Start the pomodoro server as child process
        """
        self.process_child = subprocess.Popen(["python3", "-m", "pomo"])

    def draw_gui(self):
        """
        Draw the GUI
        """
        self.master.title("Pomodoro Timer")
        self.master.geometry("300x420")

        self.mode_light()
        self.setup_styles()

        self.master.configure(bg=self.color_window_bg)

        self.create_status_icon()
        self.create_clock_label()
        self.create_pause_button()
        self.create_skip_button()
        self.create_mode_button()

    def create_status_icon(self):
        """
        Create the status icon
        """
        self.status_icon = tk.Label(
            self.master,
            text="Pause",
            fg=COLOR.RED,
            bg=self.color_window_bg,
            font=("Helvetica", 24),
        )

        self.status_icon.pack(pady=10)

    def create_pause_button(self):
        """
        Create the pause button
        """
        if self.color_window_bg == COLOR.BLACK:
            image_path = ICON.PAUSE_LIGHT
        else:
            image_path = ICON.PAUSE_DARK

        self.pause_button_image = Image.open(image_path)
        self.pause_button_image = self.pause_button_image.resize((30, 30))
        self.pause_button_image = ImageTk.PhotoImage(self.pause_button_image)

        self.pause_button = ttk.Button(
            self.master,
            image=self.pause_button_image,
            command=self.toggle_timer,
            style="Pomodoro.TButton",
        )

        self.pause_button.pack(pady=5)

    def update_pause_button(self):
        """
        Update the pause button
        """
        if self.color_window_bg == COLOR.BLACK:
            if self.status == "Pause":
                image_path = ICON.PLAY_LIGHT
            else:
                image_path = ICON.PAUSE_LIGHT
        else:
            if self.status == "Pause":
                image_path = ICON.PLAY_DARK
            else:
                image_path = ICON.PAUSE_DARK

        self.pause_button_image = Image.open(image_path)
        self.pause_button_image = self.pause_button_image.resize((30, 30))
        self.pause_button_image = ImageTk.PhotoImage(self.pause_button_image)

        self.pause_button.configure(
            image=self.pause_button_image, style="Pomodoro.TButton"
        )

    def create_skip_button(self):
        """
        Create the skip button
        """
        if self.color_window_bg == COLOR.BLACK:
            image_path = ICON.SKIP_LIGHT
        else:
            image_path = ICON.SKIP_DARK

        self.skip_button_image = Image.open(image_path)
        self.skip_button_image = self.skip_button_image.resize((30, 30))
        self.skip_button_image = ImageTk.PhotoImage(self.skip_button_image)

        self.skip_button = ttk.Button(
            self.master,
            image=self.skip_button_image,
            command=self.next_timer,
            style="Pomodoro.TButton",
        )

        self.skip_button.pack(pady=5)

    def update_skip_button(self):
        """
        Update the skip button
        """
        if self.color_window_bg == COLOR.BLACK:
            image_path = ICON.SKIP_LIGHT
        else:
            image_path = ICON.SKIP_DARK

        self.skip_button_image = Image.open(image_path)
        self.skip_button_image = self.skip_button_image.resize((30, 30))
        self.skip_button_image = ImageTk.PhotoImage(self.skip_button_image)

        self.skip_button.configure(
            image=self.skip_button_image, style="Pomodoro.TButton"
        )

    def create_clock_label(self):
        """
        Create the clock label
        """
        self.canvas = tk.Canvas(
            self.master,
            width=200,
            height=200,
            bg=self.color_window_bg,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.clock_label = tk.Label(
            self.canvas,
            text="00:00",
            fg=self.color_clock_timer,
            bg=self.color_window_bg,
            font=("Helvetica", 36),
        )

        self.canvas.create_window(100, 100, window=self.clock_label)

        self.timer_tag = tk.Label(
            self.canvas,
            text="",
            fg=self.color_timer_tag,
            bg=self.color_window_bg,
            font=("Helvetica", 12),
        )

        self.canvas.create_window(100, 135, window=self.timer_tag)

        self.clock_label.bind("<Button-2>", self.middle_click_event)
        self.clock_label.bind("<Enter>", self.clock_label.focus())
        self.clock_label.bind("<Leave>", self.master.focus())
        self.clock_label.bind("<Button-4>", self.scroll_event_pos)
        self.clock_label.bind("<Button-5>", self.scroll_event_neg)

    def scroll_event_pos(self, event):
        """
        Scroll event
        """
        self.increment_timer()

    def scroll_event_neg(self, event):
        """
        Scroll event
        """
        self.decrement_timer()

    def middle_click_event(self, event):
        """
        Middle click event
        """
        print("Middle click event")
        self.toggle_lock()

    def create_mode_button(self):
        """
        Create the mode button
        """
        if self.color_window_bg == COLOR.BLACK:
            image_path = ICON.SUN
        else:
            image_path = ICON.MOON

        self.mode_button_image = Image.open(image_path)
        self.mode_button_image = self.mode_button_image.resize((30, 30))
        self.mode_button_image = ImageTk.PhotoImage(self.mode_button_image)

        self.mode_button = ttk.Button(
            self.master,
            image=self.mode_button_image,
            command=self.toggle_mode,
            style="Pomodoro.TButton",
        )

        self.mode_button.pack(pady=5)

    def update_mode_button(self):
        """
        Update the mode button
        """
        if self.color_window_bg == COLOR.BLACK:
            image_path = ICON.SUN
        else:
            image_path = ICON.MOON

        self.mode_button_image = Image.open(image_path)
        self.mode_button_image = self.mode_button_image.resize((30, 30))
        self.mode_button_image = ImageTk.PhotoImage(self.mode_button_image)

        self.mode_button.configure(
            image=self.mode_button_image, style="Pomodoro.TButton"
        )

    def toggle_mode(self):
        """
        Toggle between light and dark mode
        """
        if self.color_window_bg == COLOR.BLACK:
            self.mode_light()
        else:
            self.mode_dark()

        # Update colors of the elements
        self.master.configure(bg=self.color_window_bg)
        self.status_icon.config(bg=self.color_window_bg)
        self.clock_label.config(fg=self.color_clock_timer, bg=self.color_window_bg)
        self.timer_tag.config(fg=self.color_timer_tag, bg=self.color_window_bg)
        self.canvas.config(bg=self.color_window_bg)

        self.setup_styles()

        self.update_mode_button()
        self.update_pause_button()
        self.update_skip_button()

    def setup_styles(self):
        """
        Setup the styles for the buttons
        """
        style = ttk.Style()
        style.configure(
            "Pomodoro.TButton",
            background=self.color_window_bg,
            foreground=self.color_button_fg,
            borderwidth=0,
            highlightthickness=0,
        )

    def mode_dark(self):
        """
        Define the colors for dark mode
        """
        self.color_window_bg = COLOR.BLACK
        self.color_button_bg = COLOR.RED
        self.color_button_fg = COLOR.WHITE
        self.color_clock_timer = COLOR.WHITE
        self.color_timer_tag = COLOR.WHITE
        self.color_arc_bg = "lightgrey"
        self.color_arc = COLOR.RED

    def mode_light(self):
        """
        Define the colors for light mode
        """
        self.color_window_bg = COLOR.WHITE
        self.color_button_bg = COLOR.GREEN
        self.color_button_fg = COLOR.BLACK
        self.color_clock_timer = COLOR.BLACK
        self.color_timer_tag = COLOR.BLACK
        self.color_arc_bg = "lightgrey"
        self.color_arc = COLOR.BLUE

    def update_progress_circle(self, time_remaining, total_time):
        """
        Update the progress circle based on the remaining time
        """
        self.canvas.delete("progress_circle")

        center_x = 100
        center_y = 100

        radius = 80

        progress_percentage = 1 - time_remaining / total_time

        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            outline=self.color_arc_bg,
            width=10,
        )

        start_angle = 90
        extent = -360 * progress_percentage

        self.canvas.create_arc(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            start=start_angle,
            extent=extent,
            style=tk.ARC,
            outline=self.color_arc,
            width=10,
            tags="progress_circle",
        )

    def display(self):
        """
        Display the timer
        """
        try:
            data = self.client.get_status()

            self.status = "Worktime" if data["status"] == "work" else "Breaktime"

            if not data["active"]:
                self.status = "Pause"

            if self.status == "Worktime":
                self.status_icon.config(fg="red")
                self.update_pause_button()

            elif self.status == "Breaktime":
                self.status_icon.config(fg="green")
                self.update_pause_button()

            else:
                self.status_icon.config(fg="blue")
                self.update_pause_button()

            self.clock_label.config(text=f"{data['timer']}")
            self.timer_tag.config(text=f"{data['tag']}")
            self.status_icon.config(text=self.status)

            self.update_progress_circle(data["remaining"], data["total_time"])

        except socket.timeout:
            self.client.reconnect()

        except json.JSONDecodeError:
            pass

        # Schedule next update in 1000ms (1 second)
        self.master.after(1000, self.display)

    def toggle_timer(self):
        """
        Toggle the timer
        """
        try:
            subprocess.run(["python3", "-m", "pomo", "toggle"])
        except Exception as e:
            print("Error occurred while executing the command:", e)

    def next_timer(self):
        """
        Skip to the next timer
        """
        try:
            subprocess.run(["python3", "-m", "pomo", "end"])
        except Exception as e:
            print("Error occurred while executing the command:", e)

    def increment_timer(self):
        """
        Increment the timer
        """
        try:
            subprocess.run(["python3", "-m", "pomo", "time", "+60"])

        except Exception as e:
            print("Error occurred while executing the command:", e)

    def decrement_timer(self):
        """
        Decrement the timer
        """
        try:
            subprocess.run(["python3", "-m", "pomo", "time", "-60"])

        except Exception as e:
            print("Error occurred while executing the command:", e)

    def toggle_lock(self):
        """
        Toggle the lock
        """
        try:
            subprocess.run(["python3", "-m", "pomo", "lock"])

        except Exception as e:
            print("Error occurred while executing the command:", e)
