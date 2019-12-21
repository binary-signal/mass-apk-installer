import os
import logging
import argparse
import time
import datetime
import shutil
from timeit import default_timer as timer

from mass_apk import logger as log
from mass_apk.adb import adb_push, adb_kill, adb_start, adb_state, APK
from mass_apk.apk import package_management, pull_apk, pkg_flags, get_package_full_path
from mass_apk.helpers import human_time, rename_fix
from mass_apk.ziptools import extract_zip, make_zip


def summary(install_state):
    success = 0
    fail = 0

    print("\n\nSummary: ")
    for s in install_state:
        if s == APK.FAILED:
            fail = fail + 1
        elif s == APK.INSTALLED:
            success = success + 1
    print(f"Installed:{success} |  Failed:{fail}")


def back_up(archive=False, encrypt=False):
    # generate filename from current date time
    backup_file = (
        str(datetime.utcnow()).split(".")[0].replace(" ", "_").replace(":", "-")
    )
    try:
        os.rmdir(backup_file)

    except FileNotFoundError:
        os.mkdir(backup_file)

    print("Listing installed apk's in device...\n")
    # get user installed packages
    pkgs = package_management(pkg_flags["user"])

    num_apk = len(pkgs)

    print("Discovering apks paths this may take a while...")
    # get full path on the android filesystem for each installed package
    paths = [get_package_full_path(pkg) for pkg in pkgs]

    # combine apk name and apk path into dictionary object
    pkgs_paths = [{pkg: paths} for pkg, path in zip(pkgs, paths)]

    print(f"\nFound {num_apk} installed packages\n")

    space = len(str(num_apk))  # calculate space for progress bar
    progress = 0
    for i in pkgs_paths:  # i is dict {package name: package path}
        progress += 1
        print(
            "[{0:{space}d}/{1:{space}d}] pulling ... {2}".format(
                progress, num_apk, i[list(i)[0]], space=space
            )
        )
        pull_apk(i)  # get apk from device

        shutil.move(
            list(i)[0] + ".apk",  # move apk to back up directory
            os.path.join(backup_file, list(i)[0] + ".apk"),
        )

    if archive:
        print(f"\nCreating zip archive: {backup_file}.zip")
        make_zip(backup_file, backup_file + ".zip")
        if os.path.exists(backup_file):
            shutil.rmtree(backup_file)

    print("\nBack up finished")


def restore(backup_path):
    clean_up = []  # list of files, dirs to delete after install

    if not os.path.exists(backup_path):
        print(f"File or folder doesn't exist {backup_path}")
        return

    if os.path.isdir(backup_path):  # install from folder
        print(f"\nRestoring back up from folder: {backup_path}")
        apk_path = backup_path

    elif os.path.isfile(backup_path):  # install from file
        filename, file_extension = os.path.splitext(backup_path)

        if ".zip" in file_extension:  # install from zip archive
            print(f"\nRestoring back up from zip file: {backup_path}")
            print(f"\nUnzipping {backup_path} ...")
            extract_zip(backup_path, filename)
            apk_path = filename
            clean_up.append(filename)

    try:
        rename_fix(apk_path)
        apks = [file for file in os.listdir(apk_path) if file.endswith(".apk")]
    except NotADirectoryError:
        print(f"isn't a dir {apk_path}")
        return

    # calculate total installation size
    size = [os.path.getsize(os.path.join(apk_path, apk)) for apk in apks]

    massapk_log.info(
        "Total Installation Size: {0:.2f} MB".format(sum(size) / (1024 * 1024))
    )
    state = []
    progress = 0

    space = len(str(len(apks)))  # calculate space for progress bar
    for apk in apks:
        progress += 1
        print(
            "[{0:{space}d}/{1:{space}d}] Installing {2}".format(
                progress, len(apks), str(apk), space=space
            )
        )
        s = adb_push(os.path.join(apk_path, apk))
        state.append(s)

    summary(state)

    for f in clean_up:
        if os.path.exists(f):
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.remove(f)
    print("\nRestore  finished")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Simple Backup / Restore  of Android apps"
    )
    subparsers = parser.add_subparsers(
        required=True, dest="command", help="command help"
    )
    parser_restore = subparsers.add_parser(
        "restore", help="restore a back up to device from path"
    )
    parser_restore.add_argument(
        "path", help="path to folder, zip file or encrypted archive backup"
    )

    parser_backup = subparsers.add_parser("backup", help="perform device back up")
    parser_backup.add_argument(
        "-o", "--outdir", help="save backup  to path", default="."
    )
    parser_backup.add_argument(
        "-a", "--archive", help="create  a zipped backup", action="store_true"
    )
    parser_backup.add_argument(
        "-e", "--encrypt", help="create an encrypted backup", action="store_true",
    )
    args = parser.parse_args()
    args = vars(args)
    command = args.pop("command")
    return command, args


def main(command, args):
    print("Apk Mass Installer Utility \nVersion: 3.1\n")

    adb_kill()  # kill any instances of adb before starting if any

    # wait for adb to detect phone
    while True:
        if adb_state():
            break
        print("No phone connected waiting to connect phone")
        time.sleep(1)

    print("Starting adb server...")
    adb_start()  # start an instance of adb server

    t_start = timer()

    if "backup" == command:
        archive = args.pop("archive", False)

        back_up(archive)

    elif "restore" == command:
        path = args.pop("path")
        restore(path)

    human_time(t_start, timer())

    adb_kill()


if __name__ == "__main__":
    command, args = parse_args()
    try:
        main(command, args)
    except KeyboardInterrupt:
        print("Received Interrupt")
