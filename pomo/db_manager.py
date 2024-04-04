#!/usr/bin/env python3

# Filename: db_manager.py
# Created on: March  6, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

from .log_manager import LogManager
from .config import DB_FILE, DB_TABLE_NAME, GMT_OFFSET


class DBManager:
    """ """

    def __init__(self, database=DB_FILE):
        self.log_manager = LogManager()
        self.database = database
        self.pending_db_update = False

    def __del__(self):
        pass

    def ensure_dir(self, file_path):
        """
        Ensure the directory of the file exists
        """
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                self.log_manager.log(f"Created directory {directory}", level="DEBUG")

            except OSError:
                self.log_manager.log(
                    f"Error creating directory {directory}", level="ERROR"
                )
                return False

        return True

    @contextmanager
    def setup_connection(self, path):
        """
        Setup the connection to the database
        """

        # check if the database exist
        path = os.path.expanduser(path)

        if not os.path.isfile(path):
            self.log_manager.log(
                f"Database {path} does not exist, creating it...", level="DEBUG"
            )

            if self.ensure_dir(path):
                try:
                    with open(path, "w") as f:
                        f.write("")

                except FileNotFoundError:
                    self.log_manager.log(
                        f"Error creating database {path}. File not found.",
                        level="ERROR",
                    )
                    exit(1)
            else:
                exit(1)

        session = sqlite3.connect(path)
        cur = session.cursor()
        self.create_table(session, cur)

        self.log_manager.log(f"Connected to database: {path}", level="INFO")

        try:
            yield cur
        finally:
            self.log_manager.log("Closing database connection", level="INFO")
            session.commit()
            session.close()

    def create_table(self, session, cursor):
        """
        Create the table in the database
        """
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS '{DB_TABLE_NAME}' (
                            date TEXT,
                            start TEXT,
                            duration INTEGER,
                            tag TEXT);
                       """
        )
        session.commit()

    def create_session(self, tag):
        """
        Create a session in the database
        """
        with self.setup_connection(self.database) as session:
            if not self.pending_db_update:
                current_time_gmt = datetime.utcnow() + timedelta(hours=GMT_OFFSET)
                formatted_date = current_time_gmt.strftime("%Y-%m-%d")
                formatted_time = current_time_gmt.strftime("%H:%M:%S")

                session.execute(
                    f"INSERT INTO '{DB_TABLE_NAME}' VALUES ('{formatted_date}', '{formatted_time}', NULL, '{tag}');"
                )
                self.log_manager.log("Created session in database", level="INFO")
                self.pending_db_update = True

    def finish_session(self, duration):
        """
        Finish the session in the database
        """
        with self.setup_connection(self.database) as session:
            if self.pending_db_update:
                session.execute(
                    f"""UPDATE '{DB_TABLE_NAME}'
                        SET duration = '{int(duration)}'
                        WHERE start IN (
                            SELECT start FROM '{DB_TABLE_NAME}'
                            ORDER BY date DESC, start DESC
                            LIMIT 1);
                    """
                )

                self.log_manager.log("Finished session in database", level="INFO")
                self.pending_db_update = False

    def update_tag(self, tag):
        """
        Update the tag in the database
        """
        with self.setup_connection(self.database) as session:
            if self.pending_db_update:
                session.execute(
                    f"""UPDATE '{DB_TABLE_NAME}'
                    SET tag = '{tag}'
                    WHERE start IN (
                        SELECT start FROM '{DB_TABLE_NAME}'
                        ORDER BY date DESC, start DESC
                        LIMIT 1);
                    """
                )

                self.log_manager.log("Updated tag in database", level="INFO")

    def perform_query(self, query):
        """
        Perform a query in the database
        """
        with self.setup_connection(self.database) as session:
            self.log_manager.log(f"Performing query: {query}", level="DEBUG")
            return session.execute(query).fetchall()
