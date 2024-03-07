#!/usr/bin/env python

# Filename: analytics.py
# Created on: March  6, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import matplotlib.pyplot as plt
import pandas as pd

from datetime import datetime


from pomo.config import DB_FILE, DB_TABLE_NAME, HOUR_FACTOR, MINUTE_FACTOR
from pomo.db_manager import DBManager


class Analytics:
    """ """

    def __init__(self):
        self.db_manager = DBManager(DB_FILE)

    def __del__(self):
        pass

    def is_date_valid(self, date):
        """ """
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def seconds_to_hours_minutes(self, seconds):
        """
        Convert seconds to hours and minutes
        """
        if seconds is None:
            return 0, 0

        hours = seconds // HOUR_FACTOR
        minutes = (seconds % HOUR_FACTOR) // MINUTE_FACTOR
        return int(hours), int(minutes)

    def query_total_sum(self, start, end):
        """
        Query the total sum of duration between start and end dates
        """
        query = f"""SELECT SUM(duration)
                    FROM '{DB_TABLE_NAME}'
                    WHERE date BETWEEN '{start}' AND '{end}'"""

        return self.db_manager.perform_query(query)

    def query_sum_per_day(self, start, end):
        """
        Query the sum of duration per day between start and end dates
        """
        query = f"""SELECT date, SUM(duration) as total_duration
                    FROM '{DB_TABLE_NAME}'
                    WHERE date BETWEEN '{start}' AND '{end}'
                    GROUP BY date"""

        return self.db_manager.perform_query(query)

    def query_sum_per_tag(self, start, end):
        """
        Query the sum of duration per tag between start and end dates
        """
        query = f"""SELECT tag, SUM(duration) as total_duration
                    FROM '{DB_TABLE_NAME}'
                    WHERE date BETWEEN '{start}' AND '{end}'
                    GROUP BY tag"""

        return self.db_manager.perform_query(query)

    def performance_between_dates(self, start, end):
        """
        Prints the performance metrics between start and end dates
        """
        if not self.is_date_valid(start) or not self.is_date_valid(end):
            print("Invalid date format")
            return

        # Query and print total sum
        total_sum = self.query_total_sum(start, end)

        # Query and print sum per day
        sum_per_day = self.query_sum_per_day(start, end)

        df = pd.DataFrame(sum_per_day, columns=["date", "total_duration"])
        df['date'] = pd.to_datetime(df['date'])
        df['total_duration_hours'] = df['total_duration'] / HOUR_FACTOR

        plt.figure(figsize=(10, 6))
        plt.bar(df['date'].dt.strftime('%Y-%m-%d'), df['total_duration_hours'], color='darkblue', label='Per Day')
        plt.axhline(y=total_sum[0][0] / HOUR_FACTOR, color='red', linestyle='--', label='Total')
        plt.title('Sum of duration per day with total')
        plt.xlabel('Date')
        plt.ylabel('Total duration (hours)')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Query and print sum per tag
        sum_per_tag = self.query_sum_per_tag(start, end)

        df = pd.DataFrame(sum_per_tag, columns=["tag", "total_duration"])
        df['total_duration_hours'] = df['total_duration'] / HOUR_FACTOR

        plt.figure(figsize=(10, 6))
        plt.bar(df['tag'], df['total_duration_hours'], color='darkblue')
        plt.title(f'Sum of duration per tag considering the period {start} to {end}')
        plt.xlabel('Tag')
        plt.ylabel('Total duration (hours)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
