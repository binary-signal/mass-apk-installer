from typing import Union, NoReturn, Optional

from massapk import adb, _logger as log
from massapk.adb import AdbError


class ApkError(AdbError):
    pass


def absolute_path(pkg_name: str) -> str:
    """
    Returns the full path of a package in android device storage
    """

    try:
        output: str = adb._exec_command(
            f"shell pm path {pkg_name}", return_stdout=True, case_sensitive=True
        )
    except AdbError as error:
        log.error(str(error) + f"Failed to retrieve full path from device for `{pkg_name}`")

    # bin returns packages name in the form
    # package:/data/app/com.dog.raider-2/base.apk
    # we need to strip package: prefix in returned string

    return output.split(":", maxsplit=1)[1].strip()
