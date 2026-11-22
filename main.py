#!/usr/bin/env python3
"""main.py -- make.fun entry for news-image-20261122.

The entry image (entry.png, a broadsheet front page summing up the world
news of Sunday 22 November 2026) is rendered ahead of time by gen.py and
shipped in this repository. This program's only job is to copy those
exact bytes to the output directory, so both grader runs produce a
byte-identical file.

Standard library only -- the grader's Python has no third-party
packages, and none are needed here.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def output_dir():
    """Where the grader wants the image: $MAKEFUN_OUTPUT_DIR or /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main():
    dest_dir = output_dir()
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    # The gate reads exactly the bytes in the file, so confirm the copy
    # landed whole before reporting success.
    if os.path.getsize(dest) != os.path.getsize(SOURCE):
        raise IOError("copy of entry.png is incomplete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
