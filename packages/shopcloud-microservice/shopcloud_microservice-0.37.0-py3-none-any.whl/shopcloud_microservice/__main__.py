import sys

from . import cli

if __name__ == "__main__":
    rc = cli.main()
    if rc != 0:
        sys.exit(rc)
