from typing import Union, NoReturn
import os
import subprocess
import time
from mass_apk import adb, logger as log
from mass_apk.adb import AdbError
from mass_apk.helpers import OS
import collections


class ApkError(AdbError):
    pass


"""
list packages [-f] [-d] [-e] [-s] [-3] [-i] [-l] [-u] [-U]
      [--show-versioncode] [--apex-only] [--uid UID] [--user USER_ID] [FILTER]
    Prints all packages; optionally only those whose name contains
    the text in FILTER.  Options are:
      -f: see their associated file
      -a: all known packages (but excluding APEXes)
      -d: filter to only show disabled packages
      -e: filter to only show enabled packages
      -s: filter to only show system packages
      -3: filter to only show third party packages
      -i: see the installer for the packages
      -l: ignored (used for compatibility with older releases)
      -U: also show the package UID
      -u: also include uninstalled packages
      --show-versioncode: also show the version code
      --apex-only: only show APEX packages
      --uid UID: filter to only show packages with the given UID
      --user USER_ID: only list packages belonging to the given user
"""


def get_package_full_path(pkg_name: str) -> Union[str, NoReturn]:
    """
    Returns the full path of a package in android device storage
    """

    try:
        output = adb._exec_command(
            f"shell pm path {pkg_name}", return_stdout=True, case_sensitive=True
        )
    except AdbError as error:
        log.error(error)
        return

    # bin returns packages name  in the form
    # package:/data/app/com.dog.raider-2/base.apk
    # we need to strip package: prefix in returned string

    if output:
        return output.split(":", maxsplit=1)[1].strip()
    log.warning(f"Failed to retrieve full path from device for `{pkg_name}`")
