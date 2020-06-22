from typing import Optional, List
import collections

from massapk import _logger as log
from massapk import adb
from massapk.adb import AdbError

__all__ = ["ApkError", "map_apk_paths", "absolute_path", "ApkAbsPath"]


class ApkError(AdbError):
    pass


ApkAbsPath = collections.namedtuple("ApkAbsPath", "name fullpath")


def map_apk_paths(apks: List[str]) -> List[ApkAbsPath]:
    abs_paths = []
    for pkg in apks:
        if pkg_abs_path := absolute_path(pkg):
            abs_paths.append((pkg, pkg_abs_path))

    # pack apk name and apk full path  into an ApkAbsPath named tuple, makes more sense to carry
    # these two variables together from now on through the back up,  comes handy
    return [ApkAbsPath(*abs_path) for abs_path in abs_paths]


def absolute_path(pkg_name: str) -> Optional[str]:
    """
    Returns the full path of a package in android device storage
    """

    try:
        output = adb.exec_command(f"shell pm path {pkg_name}", return_stdout=True, case_sensitive=True)

    except AdbError:
        log.warning(f"Path is not valid for {pkg_name}")
        return None

    # bin returns packages name in the form
    # package:/data/app/com.dog.raider-2/base.apk
    # we need to strip package: prefix in returned string
    if output:
        return output.split(":", maxsplit=1)[1].strip()
    return None
