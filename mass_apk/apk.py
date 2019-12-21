import os
import subprocess

from mass_apk.adb import adb_command, adb_path
from mass_apk.helpers import OS

# Flags for adb list packages
pkg_flags = {
    "all": "",  # list all packages
    "user": "-3",  # list 3d party packages only (default)
    "system": "-S",  # list system packages only
}




def get_package_full_path(pkg_name):
    """
    Returns the full path of a package in android device storage
    """

    state = adb_command(f"shell pm path {pkg_name}")

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

    global detected_os
    pkg_name = list(pkg_dic)

    if detected_os == OS.OSX:

        cmd = f"{adb_path} shell cat {pkg_dic[pkg_name[0]]} > base.apk"
        # cmd = "./osx/adb pull " + pkgDic[pkg_name[0]] doesn't work anymore after nougat update
    elif detected_os == OS.WIN:

        cmd = f"{adb_path} pull {pkg_dic[pkg_name[0]]}"
    elif detected_os == OS.LINUX:
        cmd = f"{adb_path} shell cat {pkg_dic[pkg_name[0]]} > base.apk"

    exit_code, output = subprocess.getstatusoutput(cmd)
    if exit_code == 0:
        if os.path.exists("base.apk"):
            os.rename("base.apk", pkg_name[0] + ".apk")


