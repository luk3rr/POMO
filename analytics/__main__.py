#!/usr/bin/env python

# Filename: __main__.py
# Created on: March  6, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import sys
from .analytics import Analytics

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 -m analytics <start_date> <end_date>")
        print("Date format: YYYY-MM-DD")
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2]

    analytics = Analytics()
    analytics.performance_between_dates(start_date, end_date)

if __name__ == "__main__":
    main()
