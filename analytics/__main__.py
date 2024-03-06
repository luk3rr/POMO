#!/usr/bin/env python

# Filename: __main__.py
# Created on: March  6, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

from .analytics import Analytics

def main():
    analytics = Analytics()
    analytics.performance_between_dates("2024-03-01", "2024-03-31")


if __name__ == "__main__":
    main()
