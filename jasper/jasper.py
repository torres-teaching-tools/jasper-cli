import argparse
import os
import sys

# Extend sys.path to include commands and utils
sys.path.append(os.path.join(os.path.dirname(__file__), "commands"))
sys.path.append(os.path.dirname(__file__))

from jasper.commands import init as init_cmd
from jasper.commands import get as get_cmd
from jasper.commands import explain as explain_cmd
from jasper.commands import crit as crit_cmd
from jasper.commands import check as check_cmd
from jasper.commands import submit as submit_cmd
from jasper.commands import badges as badges_cmd

def main():
    parser = argparse.ArgumentParser(description="Jasper CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_cmd.register(subparsers)
    get_cmd.register(subparsers)
    explain_cmd.register(subparsers)
    check_cmd.register(subparsers)
    crit_cmd.register(subparsers)
    submit_cmd.register(subparsers)
    badges_cmd.register(subparsers)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()