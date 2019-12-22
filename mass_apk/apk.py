from typing import Union, NoReturn

from mass_apk import adb, _logger as log
from mass_apk.adb import AdbError


class ApkError(AdbError):
    pass


def absolute_path(pkg_name: str) -> Union[str, NoReturn]:
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
