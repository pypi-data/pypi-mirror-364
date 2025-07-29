import sysconfig
from pathlib import Path


def _get_site_packages_location() -> Path:
    return Path(sysconfig.get_paths()["purelib"])
