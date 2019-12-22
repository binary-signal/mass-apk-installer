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
from mass_apk.apk import absolute_path
from mass_apk import AbsPath
from mass_apk.helpers import human_time, rename_fix, timed
from mass_apk.ziptools import extract, zipify
from mass_apk.apk import AdbError
from mass_apk.exceptions import MassApkFileNotFoundError


@timed
def back_up(path: os.path, list_flag: adb.AdbFlag, archive=False):
    t_start = timer()

    # get user installed packages
    pkgs = adb.list_device(list_flag)

    log.info("Discovering apk paths, this may take a while...")
    # get full path on the android filesystem for each installed package
    abs_paths = [(pkg, absolute_path(pkg)) for pkg in pkgs if absolute_path(pkg)]

    # pack apk name and apk full path  into a AbsPath named tuple, makes more sense to carry
    # these two variables together from now on through the back up,  comes handy
    parsed_paths: List[AbsPath] = [AbsPath(*abs_path) for abs_path in abs_paths]

    log.info(f"Found {len(parsed_paths)} installed packages")
    for progress, apk_item in enumerate(parsed_paths, 1):
        log.info(f"[{progress:4}/{len(parsed_paths):4}] pulling ... {apk_item.name}")
        try:
            adb.pull(apk_item.fullpath)  # get apk from device
        except AdbError:
            log.error(f"Meow here is a warning for `{apk_item.name}` apk")
        # move apk to back up directory
        else:
            if os.path.exists("base.apk"):
                # all apks retrieved with adb are saved under the same name,  `base.apk`
                # time to use a handy AbsPath named tuple to set correct name to apk pulled with adb

                # this is the correct name of the apk relative to the filesystem
                dest = os.path.join(args.path, f"{apk_item.name}.apk")
                shutil.move(f"base.apk", dest)
            else:
                log.warning("file base.apk doesn't exist - {apk_item.name}.apk ")

    if archive:
        log.info(f"Creating zip archive: {args.path}.zip, this may take a while")
        zipify(args.path, args.path + ".zip")
        shutil.rmtree(args.path)

    log.info("Back up done.")


@timed
def restore(backup_path: os.path, clean: bool):
    """

    :param backup_path:
    :param clean:bool delete folder or files used by restore command before function returns
    :return: None

    :raises MassApkFileNotFoundError
    """
    try:
        os.path.exists(backup_path)
    except FileNotFoundError as error:
        raise MassApkFileNotFoundError(
            f"Oups, the path for back file or folder ` {backup_path}` is missing !"
        )

    clean_todo = list()  # keep track of files/dir to delete before returning

    if os.path.isdir(backup_path):  # restore folder back up
        log.info(f"Restoring back up from path `{backup_path}` *  *Folder*")
        root_dir_back_up = backup_path

    else:
        root_dir_back_up = None  # we don't yet if that path will have value
        extract_to = os.path.splitext(backup_path)[0]

        if backup_path.endswith(".zip"):  # restore zip archive back up
            log.info(f"Restoring back up from path {backup_path} *  *Zip*")
            extract(zip_file=backup_path, output=extract_to)
            root_dir_back_up = extract_to  # set as path root the folder with apk extracted from zip file
            clean_todo = list([extract_to, backup_path])

    if root_dir_back_up is None:
        log.error(f"Oups not possible to extract zip file to path {extract_to} ")
        sys.exit(-1)

    apks = [file for file in os.listdir(root_dir_back_up) if file.endswith(".apk")]

    # calculate total installation size
    size = [os.path.getsize(os.path.join(root_dir_back_up, apk)) for apk in apks]

    log.info("Total Installation Size: {0:.2f} MB".format(sum(size) / (1024 * 1024)))

    for progress, apk in enumerate(apks, 1):
        log.info(f"[{progress}/{len(apks)}] Installing {apk}")
        # adb.push(os.path.join(root_dir_back_up, apk))

    if clean:

        map(
            lambda f:  shutil.rmtree(f) if os.path.isdir(f) else os.remove(f), clean_todo
        )

    log.info("Restore  done")


def parse_args() -> argparse.Namespace:
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="mass_apk")
    subparsers = parser.add_subparsers(
        title="commands", dest="command", required=True, help="help for commands"
    )

    # create sub parser for the "backup" command
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
        "-p",
        "--path",
        type=str,
        required=True,
        help="Back up File or Folder to restore from",
    )

    restore_sub.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="remove back up File or Folder defined in --path after restoration is completed ",
    )

    return parser.parse_args()


def main(args: argparse.Namespace):

    log.info("Apk Mass Installer Utility Version: 0.3.1\n")

    adb.stop_server()  # kill any instances of bin before starting if any

    # wait for bin to detect phone
    while not (state := adb.state):
        time.sleep(1)

    adb.start_server()  # start an instance of adb server

    if args.command == "backup":
        back_up(args.path, args.flag, args.archive)

    elif args.command == "restore":
        restore(args.path, args.clean)

    else:
        sys.exit(f"Unknown command {args.command}")
    adb.stop_server()


if __name__ == "__main__":
    args = parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        log.info("Received SIGINT. Quit")
