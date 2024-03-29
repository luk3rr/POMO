#!/usr/bin/env python3

# Filename: __main__.py
# Created on: March 29, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>


import tkinter as tk

from .pomo_gui import PomodoroGUI

def main():
    root = tk.Tk()
    pomodoro_gui = PomodoroGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
