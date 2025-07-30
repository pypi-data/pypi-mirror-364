import os
import re
import subprocess

from umu_commander.classes import Element, Group
from umu_commander.configuration import DB_NAME, PROTON_DIRS, UMU_PROTON_DIR


def _natural_sort_proton_ver_key(e: Element, _nsre=re.compile(r"(\d+)")):
    s: str = e.value
    return [int(text) if text.isdigit() else text for text in _nsre.split(s)]


def refresh_proton_versions():
    print("Updating umu Proton.")
    umu_update_process = subprocess.run(
        ["umu-run", '""'],
        env={"PROTONPATH": "UMU-Latest", "UMU_LOG": "debug"},
        capture_output=True,
        text=True,
    )

    for line in umu_update_process.stderr.split("\n"):
        if "PROTONPATH" in line and "/" in line:
            try:
                left: int = line.rfind("/") + 1
                print(f"Using {line[left:len(line) - 1]}.")
            except ValueError:
                print("Could not fetch latest UMU-Proton.")

            break


def _sort_proton_versions(versions: list[Element]) -> list[Element]:
    return sorted(versions, key=_natural_sort_proton_ver_key, reverse=True)


def collect_proton_versions(sort: bool = False) -> list[Group]:
    version_groups: list[Group] = []
    for proton_dir in PROTON_DIRS:
        versions: list[Element] = [
            Element(proton_dir, version, "")
            for version in os.listdir(proton_dir)
            if version != DB_NAME
        ]
        if sort:
            versions = sorted(versions, key=_natural_sort_proton_ver_key, reverse=True)

        version_groups.append(
            Group(proton_dir, f"Proton versions in {proton_dir}:", versions)
        )

    return version_groups


def get_latest_umu_proton():
    umu_proton_versions: list[Element] = [
        Element(UMU_PROTON_DIR, version, "")
        for version in os.listdir(UMU_PROTON_DIR)
        if "UMU" in version and version != DB_NAME
    ]
    umu_proton_versions = sorted(
        umu_proton_versions, key=_natural_sort_proton_ver_key, reverse=True
    )

    return umu_proton_versions[0].version_num
