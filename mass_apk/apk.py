import os
import subprocess

from mass_apk.adb import Adb
from mass_apk.helpers import OS
from mass_apk.adb import AdbError
# Flags for adb list packages

adb = Adb()

def get_package_full_path(pkg_name):
    """
    Returns the full path of a package in android device storage
    """

    global adb
    try:
        state = adb_command(f"shell pm path {pkg_name}")
    except AdbError as error:

    # adb returns packages name  in the form
    # package:/data/app/com.dog.raider-2/base.apk
    # we need to strip package: prefix in returned string

    return state.split(":")[1].strip()


def package_management(PKG_FILTER):
    """
    Lists all packages installed  in android device. Results can be
    filtered with PKG_FILTER to get only apk packages you are interested. By
    default listing only 3d party apps.
    """

    state = adb_command(f"shell pm list packages {PKG_FILTER}")

    # adb returns packages name  in the form
    # package:com.skype.raider
    # we need to strip "package:" prefix
    return [
        line.split(":")[1].strip()
        for line in state.lower().splitlines()
        if line.startswith("package:")
    ]


def pull_apk(pkg_dic):
    """
    Pulls apk specified in pkgDic variable from android device using adb
    renames extracted apk to filename specified in pkgDic key value pair.
    """

    pkg_name = list(pkg_dic)


    cmd = f" pull {pkg_dic[pkg_name[0]]}"

    exit_code, output = subprocess.getstatusoutput(cmd)
    if exit_code == 0:
        if os.path.exists("base.apk"):
            os.rename("base.apk", pkg_name[0] + ".apk")
