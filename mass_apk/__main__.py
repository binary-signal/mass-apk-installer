from typing import List, Dict, Union
import os
import logging
import sys
import argparse

import time
import datetime as dt
import shutil
from timeit import default_timer as timer

from mass_apk import logger as log
from mass_apk import adb
from mass_apk.apk import get_package_full_path
from mass_apk import Apkitem
from mass_apk.helpers import human_time, rename_fix, timed
from mass_apk.ziptools import extract_zip, make_zip
from mass_apk.apk import AdbError


@timed
def back_up(path, list_flag: adb.AdbFlag, archive=False):
    t_start = timer()

    # get user installed packages
    pkgs = adb.list_device(list_flag)

    log.info("Discovering apk paths, this may take a while...")
    # get full path on the android filesystem for each installed package
    pkg_paths = list()
    for pkg in pkgs:
        if path := get_package_full_path(pkg):
            pkg_paths.append((pkg, path))

    # map apk name and apk path
    mapped_pkg: List[Apkitem] = [Apkitem(*p) for p in pkg_paths]

    log.info(f"Found {len(mapped_pkg)} installed packages")
    for progress, apk_item in enumerate(mapped_pkg, 1):
        log.info(f"[{progress:4}/{len(mapped_pkg):4}] pulling ... {apk_item.name}")
        try:
            adb.pull(apk_item.fullpath)  # get apk from device
        except AdbError:
            pass
        # move apk to back up directory
        else:
            if os.path.exists("base.apk"):
                dest = os.path.join(args.path, f"{apk_item.name}.apk")
                shutil.move(f"base.apk", dest)
            else:
                log.warning("file base.apk not found")

    if archive:
        log.info(f"Creating zip archive: {args.path}.zip, this may take a while")
        make_zip(args.path, args.path + ".zip")
        shutil.rmtree(args.path)

    log.info("Back up done.")


def restore(backup_path):
    t_start = timer()
    clean_up = []  # list of files, dirs to delete after install

    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"File or folder doesn't exist {backup_path}")

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

    log.info("Total Installation Size: {0:.2f} MB".format(sum(size) / (1024 * 1024)))
    state = []

    for progress, apk in enumerate(apks, 1):
        print(
            "[{0:{space}d}/{1:{space}d}] Installing {2}".format(
                progress, len(apks), str(apk)
            )
        )
        s = adb.push(os.path.join(apk_path, apk))
        state.append(s)

    for f in clean_up:
        if os.path.exists(f):
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.remove(f)
    human_time(t_start, timer())
    print("\nRestore  finished")


def parse_args():
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="massapk")
    parser.add_argument("--foo", action="store_true", help="help for foo arg.")
    subparsers = parser.add_subparsers(
        title="commands", dest="command", help="help for commands", required=True
    )

    # create the parser for the "backup" command
    backup_sub = subparsers.add_parser("backup", help="backup help")
    backup_sub.add_argument(
        "-f",
        "--flag",
        type=adb.AdbFlag,
        default=adb.AdbFlag.USER,
        help="Specify which apks to backup. Defaults to  user apks."
        "Can be overriden to back up system apks with SYS or all apks with ALL",
    )

    backup_sub.add_argument(
        "-p",
        "--path",
        type=str,
        default=os.getcwd(),
        help="Folder or Path on filesystem to save back up",
    )
    backup_sub.add_argument(
        "-a",
        "--archive",
        action="store_true",
        help="compress back up folder into zip file",
    )

    # create the parser for the "restore" command
    restore_sub = subparsers.add_parser("restore", help="help for restore")
    restore_sub.add_argument(
        "-p", "--path", type=str, help="Back up File or Folder to restore from"
    )

    args = parser.parse_args()
    return args


def main(args):
    print(args)
    print("Apk Mass Installer Utility \nVersion: 0.3.1\n")

    adb.stop_server()  # kill any instances of bin before starting if any

    # wait for bin to detect phone
    while not (state := adb.state):
        time.sleep(1)

    adb.start_server()  # start an instance of bin server

    if command := args.command == "backup":
        try:
            os.mkdir(args.path)
        except FileExistsError:
            log.warning("Back up destination already exists !")

        back_up(args.path, args.flag, args.archive)

    elif command == "restore":
        try:
            os.path.exists(args.path)
        except FileNotFoundError:
            log.error(
                f"Back Folder or Path doesn't exit. Path {(os.path.abspath(args.path))}"
            )
            sys.exit(-1)

        restore(args.path)

    adb.stop_server()


if __name__ == "__main__":
    args = parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        print("Received Interrupt")
