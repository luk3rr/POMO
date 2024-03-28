#!/usr/bin/env python3

# Filename: __main__.py
# Created on: March  2, 2024
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

import sys
import time

from .polypomo import PolyPomo

def main():
    """
    Main function
    """

    with PolyPomo() as polypomo:
        while True:
            time.sleep(1)

            try:
                msg = polypomo.display()

                if msg:
                    sys.stdout.write(msg)
                    sys.stdout.flush()

            except Exception as e:
                sys.stderr.write(f"Fatal error: {e}\n")
                sys.stderr.flush()
                sys.exit(1)

if __name__ == "__main__":
    main()
