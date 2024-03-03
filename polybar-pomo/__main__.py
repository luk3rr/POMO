#!/usr/bin/env python3

# Filename: __main__.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import sys
import time
import json
import socket

from .integration import Integration


def main():
    """
    Main function
    """

    with Integration() as integration:
        while True:
            time.sleep(1)

            try:
                msg = integration.get_status()
                sys.stdout.write(msg)
                sys.stdout.flush()

            except socket.timeout:
                print(f"Connection lost. Reconnecting...")
                integration.reconnect()
                continue

            except json.JSONDecodeError:
                # print(f"Failed to decode data")
                continue

            except Exception as e:
                sys.stderr.write(f"Fatal error: {e}\n")
                sys.stderr.flush()
                sys.exit(1)


if __name__ == "__main__":
    main()
