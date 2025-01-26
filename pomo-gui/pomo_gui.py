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
from pomo.config import ICON

from .config import COLOR, DRACULA_THEME
from .config import WINDOW, CLOCK, TAG, ARC, BUTTON


class PomodoroGUI:
    def __init__(self, master, args):
        self.master = master
        self.args = args
        self.darkmode = args.darkmode

        if args.client:
            self.client = Client()
        else:
            self.start_pomo_server()
            self.client = Client()

        self.status = "Pause"
        self.draw_gui()
        self.display()

    def __del__(self):
        if not self.args.client and self.process_child:
            # Terminates the process
            self.process_child.terminate()

    def start_pomo_server(self):
        """
        Start the pomodoro server as child process
        """

        self.process_child = subprocess.Popen(
            [
                "python3",
                "-m",
                "pomo",
                "--worktime",
                str(self.args.worktime),
                "--breaktime",
                str(self.args.breaktime),
                "--database",
                str(self.args.database),
                "--tag",
                str(self.args.tag),
            ]
        )

    def draw_gui(self):
        """
        Draw the GUI
        """
        self.master.title(WINDOW.TITLE)
        self.master.geometry(WINDOW.SIZE)

        if self.args.darkmode:
            self.mode_dark()

        else:
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
            font=(WINDOW.FONT, WINDOW.FONT_SIZE),
        )

        self.status_icon.pack(pady=10)

    def create_pause_button(self):
        """
        Create the pause button
        """
        if self.darkmode:
            image_path = ICON.PAUSE_LIGHT
        else:
            image_path = ICON.PAUSE_DARK

        self.pause_button_image = Image.open(image_path)
        self.pause_button_image = self.pause_button_image.resize(BUTTON.IMG_SIZE)
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
        if self.darkmode:
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
        self.pause_button_image = self.pause_button_image.resize(BUTTON.IMG_SIZE)
        self.pause_button_image = ImageTk.PhotoImage(self.pause_button_image)

        self.pause_button.configure(
            image=self.pause_button_image, style="Pomodoro.TButton"
        )

    def create_skip_button(self):
        """
        Create the skip button
        """
        if self.darkmode:
            image_path = ICON.SKIP_LIGHT
        else:
            image_path = ICON.SKIP_DARK

        self.skip_button_image = Image.open(image_path)
        self.skip_button_image = self.skip_button_image.resize(BUTTON.IMG_SIZE)
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
        if self.darkmode:
            image_path = ICON.SKIP_LIGHT
        else:
            image_path = ICON.SKIP_DARK

        self.skip_button_image = Image.open(image_path)
        self.skip_button_image = self.skip_button_image.resize(BUTTON.IMG_SIZE)
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
            width=CLOCK.SIZE[0],
            height=CLOCK.SIZE[1],
            bg=self.color_window_bg,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.clock_label = tk.Label(
            self.canvas,
            text="00:00",
            fg=self.color_clock_timer,
            bg=self.color_window_bg,
            font=(WINDOW.FONT, CLOCK.FONT_SIZE),
        )

        self.canvas.create_window(
            CLOCK.WINDOW_SIZE[0], CLOCK.WINDOW_SIZE[1], window=self.clock_label
        )

        self.timer_tag = tk.Label(
            self.canvas,
            text="",
            fg=self.color_timer_tag,
            bg=self.color_window_bg,
            font=(WINDOW.FONT, TAG.FONT_SIZE),
        )

        self.canvas.create_window(
            TAG.WINDOW_SIZE[0], TAG.WINDOW_SIZE[1], window=self.timer_tag
        )

        # Mouse events
        self.timer_tag.bind("<Button-1>", self.edit_tag)
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

    def edit_tag(self, event):
        """
        Allow editing of the tag text.
        """
        # Replace the label with an entry widget
        self.timer_entry = tk.Entry(
            self.canvas,
            fg=self.color_timer_tag,
            bg=self.color_window_bg,
            font=(WINDOW.FONT, TAG.FONT_SIZE),
        )
        self.timer_entry.insert(
            0, self.timer_tag.cget("text")
        )  # Pre-fill with current text
        # Save on Enter
        self.timer_entry.bind("<Return>", self.save_tag)

        # Cancel edit
        self.timer_entry.bind("<FocusOut>", self.cancel_tag_edit)
        self.timer_entry.bind("<Escape>", self.cancel_tag_edit)

        self.canvas.create_window(TAG.WINDOW_SIZE[0], TAG.WINDOW_SIZE[1], window=self.timer_entry)
        self.timer_entry.focus()

    def cancel_tag_edit(self, event):
        """
        Cancel the tag edit.
        """
        self.timer_entry.destroy()

    def save_tag(self, event):
        """
        Save the edited tag text and execute a command.
        """
        old_text = self.timer_tag.cget("text")
        new_text = self.timer_entry.get()
        self.timer_tag.config(text=new_text)  # Update the label
        self.timer_entry.destroy()  # Remove the entry widget

        new_text = new_text.strip()  # Remove leading/trailing whitespace

        # do nothing if the text is empty or unchanged
        if not new_text or new_text == old_text:
            return

        try:
            subprocess.run(["python3", "-m", "pomo", "tag", new_text])
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

    def middle_click_event(self, event):
        """
        Middle click event
        """
        self.toggle_lock()

    def create_mode_button(self):
        """
        Create the mode button
        """
        if self.darkmode:
            image_path = ICON.SUN
        else:
            image_path = ICON.MOON

        self.mode_button_image = Image.open(image_path)
        self.mode_button_image = self.mode_button_image.resize(BUTTON.IMG_SIZE)
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
        if self.darkmode:
            image_path = ICON.SUN
        else:
            image_path = ICON.MOON

        self.mode_button_image = Image.open(image_path)
        self.mode_button_image = self.mode_button_image.resize(BUTTON.IMG_SIZE)
        self.mode_button_image = ImageTk.PhotoImage(self.mode_button_image)

        self.mode_button.configure(
            image=self.mode_button_image, style="Pomodoro.TButton"
        )

    def toggle_mode(self):
        """
        Toggle between light and dark mode
        """
        if self.darkmode:
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
        self.darkmode = True
        self.color_window_bg = DRACULA_THEME.BACKGROUND
        self.color_button_bg = DRACULA_THEME.BACKGROUND
        self.color_button_fg = DRACULA_THEME.FOREGROUND
        self.color_clock_timer = DRACULA_THEME.FOREGROUND
        self.color_timer_tag = DRACULA_THEME.FOREGROUND
        self.color_arc_bg = DRACULA_THEME.CURRENT_LINE
        self.color_arc = DRACULA_THEME.CYAN
        self.status_icon_worktime_fg = DRACULA_THEME.RED
        self.status_icon_breaktime_fg = DRACULA_THEME.GREEN
        self.status_icon_pause_fg = DRACULA_THEME.PINK

    def mode_light(self):
        """
        Define the colors for light mode
        """
        self.darkmode = False
        self.color_window_bg = COLOR.WHITE
        self.color_button_bg = COLOR.GREEN
        self.color_button_fg = COLOR.BLACK
        self.color_clock_timer = COLOR.BLACK
        self.color_timer_tag = COLOR.BLACK
        self.color_arc_bg = COLOR.GRAY
        self.color_arc = COLOR.BLUE
        self.status_icon_worktime_fg = COLOR.RED
        self.status_icon_breaktime_fg = COLOR.GREEN
        self.status_icon_pause_fg = COLOR.BLUE

    def update_progress_circle(self, time_remaining, total_time):
        """
        Update the progress circle based on the remaining time
        """
        self.canvas.delete(ARC.TAG)

        progress_percentage = 1 - time_remaining / total_time

        self.canvas.create_oval(
            ARC.CENTER[0] - ARC.RADIUS,
            ARC.CENTER[1] - ARC.RADIUS,
            ARC.CENTER[0] + ARC.RADIUS,
            ARC.CENTER[1] + ARC.RADIUS,
            outline=self.color_arc_bg,
            width=ARC.WIDTH,
        )

        self.canvas.create_arc(
            ARC.CENTER[0] - ARC.RADIUS,
            ARC.CENTER[1] - ARC.RADIUS,
            ARC.CENTER[0] + ARC.RADIUS,
            ARC.CENTER[1] + ARC.RADIUS,
            start=ARC.START_ANGLE,
            extent=-ARC.EXTEND_ANGLE * progress_percentage,
            style=tk.ARC,
            outline=self.color_arc,
            width=ARC.WIDTH,
            tags=ARC.TAG,
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
                self.status_icon.config(fg=self.status_icon_worktime_fg)
                self.update_pause_button()

            elif self.status == "Breaktime":
                self.status_icon.config(fg=self.status_icon_breaktime_fg)
                self.update_pause_button()

            else:
                self.status_icon.config(fg=self.status_icon_pause_fg)
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
        self.master.after(WINDOW.UPDATE_INTERVAL_MS, self.display)

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
