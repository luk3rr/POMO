#!/usr/bin/env python3

# Filename: __main__.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import sys
import time

from .integration import Integration


def main():
    """
    Main function
    """

    integration = Integration()

    while True:
        time.sleep(1)
        msg = integration.get_status()

        sys.stdout.write(msg)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
