import shutil

from umu_commander import db
from umu_commander.classes import Group
from umu_commander.configuration import *
from umu_commander.proton import (
    collect_proton_versions,
    get_latest_umu_proton,
    refresh_proton_versions,
)
from umu_commander.util import (
    get_selection,
)


def untrack(quiet: bool = False):
    current_dir: str = os.getcwd()
    for proton_dir in db.copy().keys():
        for proton_ver in db.get(proton_dir):
            db.remove_from(proton_dir, proton_ver, current_dir)

    if not quiet:
        print("Directory removed from all user lists.")


def track(proton: Element = None, refresh_versions: bool = True, quiet: bool = False):
    if refresh_versions:
        refresh_proton_versions()

    if proton is None:
        proton: Element = get_selection(
            "Select Proton version to add directory as user:",
            None,
            collect_proton_versions(sort=True),
        )

    untrack(quiet=True)
    current_directory: str = os.getcwd()
    db.add_to(proton.dir, proton.version_num, current_directory)

    if not quiet:
        print(
            f"Directory {current_directory} added to Proton version's {proton.version_num} in {proton.dir} user list."
        )


def users():
    proton_version_dirs: list[Group] = collect_proton_versions(sort=True)

    for proton_dir in proton_version_dirs:
        for proton in proton_dir.versions:
            if proton.version_num in db.get(proton.dir):
                proton.user_count = (
                    "(" + str(len(db.get(proton.dir, proton.version_num))) + ")"
                )
            else:
                proton.user_count = "(-)"

    proton: Element = get_selection(
        "Select Proton version to view user list:", None, proton_version_dirs
    )

    if proton.dir in db.copy() and proton.version_num in db.get(proton.dir):
        version_users: list[str] = db.get(proton.dir, proton.version_num)
        if len(version_users) > 0:
            print(f"Directories using {proton.version_num} of {proton.dir}:")
            print(*version_users, sep="\n")
        else:
            print("No directories currently use this version.")
    else:
        print("This version hasn't been used by umu before.")


def delete():
    for proton_dir in db.copy().keys():
        for proton_ver, version_users in db.get(proton_dir).copy().items():
            if proton_ver == get_latest_umu_proton():
                continue

            if len(version_users) == 0:
                selection: str = input(
                    f"{proton_ver} in {proton_dir} has no using directories, delete? (Y/N) ? "
                )
                if selection.lower() == "y":
                    try:
                        shutil.rmtree(os.path.join(proton_dir, proton_ver))
                    except FileNotFoundError:
                        pass
                    db.delete(proton_dir, proton_ver)


def untrack_unlinked():
    for proton_dir in db.copy().keys():
        for proton_ver, version_users in db.get(proton_dir).items():
            for user in version_users:
                if not os.path.exists(user):
                    db.remove_from(proton_dir, proton_ver, user)
