import subprocess
import tomllib
from collections.abc import Mapping
from typing import Any

from umu_commander import tracking
from umu_commander.configuration import *
from umu_commander.proton import collect_proton_versions, refresh_proton_versions
from umu_commander.util import (
    get_selection,
    values_to_elements,
)


def _write(params: Mapping[str, Any]):
    config: str = "[umu]\n"
    for key in set(params.keys()) - {"env", "launch_args"}:
        config += f'{key} = "{params[key]}"\n'

    config += f"launch_args = {params["launch_args"]}\n"

    config += "\n[env]\n"
    for key, value in params["env"].items():
        config += f'{key} = "{value}"\n'

    config_file = open(CONFIG_NAME, "wt")
    config_file.write(config)
    config_file.close()


def create():
    refresh_proton_versions()

    params: dict[str, Any] = {"env": {}}

    # Prefix selection
    selection: str = get_selection(
        "Select wine prefix:",
        values_to_elements([*os.listdir(PREFIX_DIR), "Current directory"]),
        None,
    ).value

    if selection == "Current directory":
        params["prefix"] = os.path.join(os.getcwd(), "prefix")
    else:
        params["prefix"] = os.path.join(PREFIX_DIR, selection)

    # Proton selection
    selected_umu_latest: bool = False
    proton: Element = get_selection(
        "Select Proton version:",
        values_to_elements(["Always latest UMU Proton"]),
        [*collect_proton_versions(sort=True)],
    )
    if proton.value == "Always latest UMU Proton":
        selected_umu_latest = True
    else:
        params["proton"] = os.path.join(proton.dir, proton.version_num)

    # Select DLL overrides
    possible_overrides: list[Element] = [
        Element(info="Reset"),
        Element(info="Done"),
        *DLL_OVERRIDES_OPTIONS,
    ]
    selected: set[int] = set()
    while True:
        print("Select DLLs to override, you can select multiple:")
        for idx, override in enumerate(possible_overrides):
            if idx in selected:
                idx = "Y"
            print(f"{idx}) {override.info}")

        try:
            index: int = int(input("? "))
            print("")
        except ValueError:
            continue

        if index == 0:
            selected = set()
            continue

        if index == 1:
            break

        index: int = int(index)
        if index - 1 < len(possible_overrides):
            selected.add(index)

    if len(selected) > 0:
        params["env"]["WINEDLLOVERRIDES"] = ""
        for selection in selected:
            # noinspection PyTypeChecker
            params["env"]["WINEDLLOVERRIDES"] += possible_overrides[selection].value

    # Set language locale
    match get_selection(
        "Select locale:",
        values_to_elements(["Default", "Japanese"]),
        None,
    ).value:
        case "Default":
            pass
        case "Japanese":
            params["env"]["LANG"] = "ja_JP.UTF8"

    # Input executable launch args
    launch_args: list[str] = input(
        "Enter executable options, separated by spaces:\n? "
    ).split()
    params["launch_args"] = launch_args

    # Select executable name
    files: list[str] = [
        file
        for file in os.listdir(os.getcwd())
        if os.path.isfile(os.path.join(os.getcwd(), file))
    ]
    executable_name: str = get_selection(
        "Select game executable:", values_to_elements(files), None
    ).value
    params["exe"] = executable_name

    try:
        _write(params)
        print(f"Configuration file {CONFIG_NAME} created at {os.getcwd()}.")
        print(f"Use by running umu-commander run.")
        if not selected_umu_latest:
            tracking.track(proton, False)
    except:
        print("Could not create configuration file.")


def run():
    with open(CONFIG_NAME, "rb") as toml_file:
        # noinspection PyTypeChecker
        config = tomllib.load(toml_file)

        if not os.path.exists(config["umu"]["prefix"]):
            os.mkdir(config["umu"]["prefix"])

        os.environ.update(config.get("env", {}))
        subprocess.run(
            args=["umu-run", "--config", CONFIG_NAME],
            env=os.environ,
        )
