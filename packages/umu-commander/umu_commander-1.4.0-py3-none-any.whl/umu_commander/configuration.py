import os
from pathlib import Path

from umu_commander.classes import Element

PROTON_DIRS: list[str] = [
    os.path.join(Path.home(), ".local/share/Steam/compatibilitytools.d/"),
    os.path.join(Path.home(), ".local/share/umu/compatibilitytools"),
]
# where UMU saves its UMU-Proton versions
UMU_PROTON_DIR: str = os.path.join(
    Path.home(), ".local/share/Steam/compatibilitytools.d/"
)
DB_NAME: str = "tracking.json"
DB_DIR: str = os.path.join(Path.home(), ".local/share/umu/compatibilitytools")
CONFIG_NAME: str = "umu-config.toml"
# default WINE prefix directory
PREFIX_DIR: str = os.path.join(Path.home(), ".local/share/wineprefixes/")
# Label, override string, follow the example
DLL_OVERRIDES_OPTIONS: list[Element] = [
    Element(info="winhttp for BepInEx", value="winhttp.dll=n;")
]
