from typing import List

import os
import sys
import shutil


from massapk import adb, ApkAbsPath
from massapk import _logger as log
from massapk.apk import absolute_path, AdbError
from massapk.exceptions import MassApkFileNotFoundError
from massapk.helpers import elapsed_time
from massapk.ziptools import unzippify, zipify


@elapsed_time
def back_up(path: os.path, list_flag: adb.Flag, archive=False):

    try:
        os.makedirs(path)
    except FileExistsError:
        log.warning("Back up destination already exists ")

    # get user installed packages
    pkgs = adb.list_device(list_flag)

    log.info("Discovering apk paths, this may take a while...")
    # get full path on the android filesystem for each installed package
    abs_paths = [(pkg, absolute_path(pkg)) for pkg in pkgs if absolute_path(pkg)]

    # pack apk name and apk full path  into an ApkAbsPath named tuple, makes more sense to carry
    # these two variables together from now on through the back up,  comes handy
    parsed_paths: List[ApkAbsPath] = [ApkAbsPath(*abs_path) for abs_path in abs_paths]

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
                dest = os.path.join(path, f"{apk_item.name}.apk")
                shutil.move(f"base.apk", dest)
            else:
                log.warning("file base.apk doesn't exist - {apk_item.name}.apk ")

    if archive:
        log.info(f"Creating zip archive: {path}.zip, this may take a while")
        zipify(path, path + ".zip")
        shutil.rmtree(path)

    log.info("Back up done.")


@elapsed_time
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

    cleanup_todo = list()  # keep track of files/dir to delete before returning

    if os.path.isdir(backup_path):  # restore a folder back up
        log.info(f"Restoring back up from path `{backup_path}` *  *Folder*")
        root_dir_back_up = backup_path

    else:
        root_dir_back_up = None  # we don't yet if that path will have value
        extract_to = os.path.splitext(backup_path)[0]

        if backup_path.endswith(".zip"):  # restore a zip archive back up
            log.info(f"Restoring back up from path {backup_path} *  *Zip*")
            unzippify(zip_file=backup_path, output=extract_to)
            root_dir_back_up = extract_to  # set as path root the folder with apk extracted from zip file
            cleanup_todo = list([extract_to, backup_path])

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
            lambda f: shutil.rmtree(f) if os.path.isdir(f) else os.remove(f), cleanup_todo
        )

    log.info("Restore  done")
