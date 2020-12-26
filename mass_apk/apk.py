"""Common operation and manipulation for paths in android devices"""

from typing import  List
import collections
import logging

from mass_apk import adb
from mass_apk.adb import AdbError
from mass_apk.exceptions import MassApkError

__all__ = ["ApkError", "map_apk_paths", "absolute_path", "ApkAbsPath"]

log = logging.getLogger(__name__)


class ApkError(AdbError):
    """Base exception class for `apk` module."""


ApkAbsPath = collections.namedtuple("ApkAbsPath", "name fullpath")


def map_apk_paths(apks: List[str]) -> List[ApkAbsPath]:
    """Get mapping for a list of packages.

    Return a dict object with key package name and value absolute
    path package.

    """
    abs_paths = []
    for pkg in apks:
        try:
            if pkg_abs_path := absolute_path(pkg):
                abs_paths.append((pkg, pkg_abs_path))
        except MassApkError as error:
            log.error(error)
    # pack apk name and apk full path  into an ApkAbsPath named tuple, makes more sense to carry
    # these two variables together from now on through the back up,  comes handy
    return [ApkAbsPath(*abs_path) for abs_path in abs_paths]


def absolute_path(pkg_name: str) -> str:
    """Return full path of a package in android device storage."""
    try:
        output = adb.exec_command(
            f"shell pm path {pkg_name}", return_stdout=True, case_sensitive=True
        )

    except AdbError:
        raise MassApkError("Path is not valid for {0}".format( pkg_name))

    # bin returns packages name in the form
    # package:/data/app/com.dog.raider-2/base.apk
    # we need to strip package: prefix in returned string
    if output and output.startswith("package:"):
        return output.split(":", maxsplit=1)[1].strip()

    raise MassApkError("Path is not valid for %s %s", pkg_name, output)
