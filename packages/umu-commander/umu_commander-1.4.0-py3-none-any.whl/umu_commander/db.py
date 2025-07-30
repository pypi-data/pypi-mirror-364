import json
from collections import defaultdict
from json import JSONDecodeError

from umu_commander.configuration import *

_db: defaultdict[str, defaultdict[str, list[str]]]


def load():
    global _db

    if not os.path.exists(DB_DIR):
        os.mkdir(DB_DIR)

    try:
        with open(os.path.join(DB_DIR, DB_NAME), "rt") as db_file:
            _db = defaultdict(lambda: defaultdict(list))
            _db.update(json.load(db_file))

    except JSONDecodeError:
        print(f"Could not decode DB file, is it valid JSON?")
        raise JSONDecodeError("", "", 0)

    except FileNotFoundError:
        _db = defaultdict(lambda: defaultdict(list))


def dump():
    with open(os.path.join(DB_DIR, DB_NAME), "wt") as db_file:
        # noinspection PyTypeChecker
        json.dump(_db, db_file, indent="\t")


def copy():
    return _db.copy()


def get(proton_dir: str, proton_ver: str = None) -> dict[str, list[str]] | list[str]:
    if proton_ver is None:
        return _db[proton_dir]

    return _db[proton_dir][proton_ver]


# add user_dir to proton_ver's of proton_dir list of users
def add_to(proton_dir: str, proton_ver: str, user_dir: str):
    global _db

    if proton_ver not in _db[proton_dir]:
        _db[proton_dir][proton_ver] = []

    _db[proton_dir][proton_ver].append(user_dir)


def remove_from(proton_dir: str, proton_ver: str, user_dir: str):
    global _db

    if user_dir in _db[proton_dir][proton_ver]:
        _db[proton_dir][proton_ver].remove(user_dir)


def delete(proton_dir: str, proton_ver: str):
    global _db

    del _db[proton_dir][proton_ver]
