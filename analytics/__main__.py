#!/usr/bin/env python

# Filename: __main__.py
# Created on: March  6, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import sys
from datetime import datetime, timedelta
from .analytics import Analytics

def get_date_range(current_date, days_before):
    """
    Get the date range
    """
    start_date = current_date - timedelta(days=days_before)
    end_date = current_date

    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def main():
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python3 -m analytics <start_date> <end_date>")
        print("Usage: python3 -m analytics <n days before> # to get the range from n days before to today")
        print("Date format: YYYY-MM-DD")
        sys.exit(1)


    if len(sys.argv) == 2:
        days_before = int(sys.argv[1])

        assert days_before > 0, "Days before must be greater than 0"

        current_date = datetime.now()
        start_date, end_date = get_date_range(current_date, days_before)

    elif len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]

    analytics = Analytics()

    analytics.performance_between_dates(start_date, end_date)

if __name__ == "__main__":
    main()
