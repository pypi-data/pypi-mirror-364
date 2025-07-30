#!/usr/bin/python3
import sys
from json import JSONDecodeError

from umu_commander import db, tracking, umu_config
from umu_commander.configuration import *


def print_help():
    print(
        "umu-commander is an interactive CLI tool to help you manage Proton versions used by umu, as well as create enhanced launch configs.",
        "",
        "For details, explanations, and more, see the README.md file, or visit https://github.com/Mpaxlamitsounas/umu-commander.",
        sep="\n",
    )


def main() -> int:
    try:
        db.load()
    except JSONDecodeError:
        print(f"Tracking file at {os.path.join(DB_DIR, DB_NAME)} could not be read.")
        return 2

    if len(sys.argv) == 1:
        print_help()
        return 0

    verb: str = sys.argv[1]
    match verb:
        case "track":
            tracking.track()
        case "untrack":
            tracking.untrack()
        case "users":
            tracking.users()
        case "delete":
            tracking.delete()
        case "create":
            umu_config.create()
        case "run":
            umu_config.run()
        case _:
            print("Invalid verb.")
            print_help()
            return 3

    tracking.untrack_unlinked()
    db.dump()

    return 0


if __name__ == "__main__":
    exit(main())
